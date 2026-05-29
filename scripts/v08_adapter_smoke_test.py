from __future__ import annotations

import sys
from pathlib import Path

# Allow running this script from the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.model_adapters import (
    BASE_URL_ENV_NAME,
    MAX_TOKENS_ENV_NAME,
    MODEL_ENV_NAME,
    TEMPERATURE_ENV_NAME,
    TIMEOUT_SECONDS_ENV_NAME,
    API_KEY_ENV_NAME,
    MockModelAdapter,
    ModelAdapterError,
    OpenAICompatibleAdapter,
    OpenAICompatibleConfig,
    generate_responses_for_cases,
    get_adapter_options,
    openai_compatible_http_request,
)


def assert_raises_model_adapter_error(callable_to_test) -> str:
    try:
        callable_to_test()
    except ModelAdapterError as exc:
        return str(exc)

    raise AssertionError("Expected ModelAdapterError to be raised.")


def valid_config_source() -> dict[str, str]:
    return {
        API_KEY_ENV_NAME: "test-api-key",
        BASE_URL_ENV_NAME: "https://example.test/v1",
        MODEL_ENV_NAME: "test-model",
        TIMEOUT_SECONDS_ENV_NAME: "10",
        MAX_TOKENS_ENV_NAME: "128",
        TEMPERATURE_ENV_NAME: "0.2",
    }


def test_missing_api_key_raises() -> None:
    env = valid_config_source()
    env[API_KEY_ENV_NAME] = ""

    message = assert_raises_model_adapter_error(
        lambda: OpenAICompatibleConfig.from_sources(env=env)
    )

    assert "missing an API key" in message
    print("Missing API key smoke test passed.")


def test_missing_model_raises() -> None:
    env = valid_config_source()
    env[MODEL_ENV_NAME] = ""

    message = assert_raises_model_adapter_error(
        lambda: OpenAICompatibleConfig.from_sources(env=env)
    )

    assert "missing a model" in message
    print("Missing model smoke test passed.")


def test_valid_config_without_network_call() -> None:
    config = OpenAICompatibleConfig.from_sources(env=valid_config_source())

    assert config.api_key == "test-api-key"
    assert config.base_url == "https://example.test/v1"
    assert config.model == "test-model"
    assert config.timeout_seconds == 10.0
    assert config.max_tokens == 128
    assert config.temperature == 0.2
    assert "test-api-key" not in repr(config)
    assert "<redacted>" in repr(config)

    print("Valid OpenAI-compatible config smoke test passed.")


def test_adapter_does_not_make_real_api_calls() -> None:
    config = OpenAICompatibleConfig.from_sources(env=valid_config_source())
    adapter = OpenAICompatibleAdapter(config)

    assert adapter.enabled is False
    message = assert_raises_model_adapter_error(
        lambda: adapter.generate_response("Test prompt")
    )
    assert "API execution is not enabled" in message

    print("OpenAI-compatible adapter no-execution smoke test passed.")


def test_fake_transport_returns_response_text() -> None:
    config = OpenAICompatibleConfig.from_sources(env=valid_config_source())

    def fake_transport(payload, headers):
        return {
            "choices": [
                {
                    "message": {
                        "content": "Fake transport response.",
                    }
                }
            ]
        }

    adapter = OpenAICompatibleAdapter(config, request_fn=fake_transport)
    response = adapter.generate_response("Hello from the test prompt.")

    assert response == "Fake transport response."
    print("Fake transport response smoke test passed.")


def test_fake_transport_receives_expected_payload_and_headers() -> None:
    config = OpenAICompatibleConfig.from_sources(env=valid_config_source())
    captured = {}

    def fake_transport(payload, headers):
        captured["payload"] = payload
        captured["headers"] = headers
        return {
            "choices": [
                {
                    "message": {
                        "content": "Captured payload response.",
                    }
                }
            ]
        }

    adapter = OpenAICompatibleAdapter(config, request_fn=fake_transport)
    response = adapter.generate_response("Check this payload.")

    assert response == "Captured payload response."
    assert captured["payload"]["model"] == "test-model"
    assert captured["payload"]["messages"] == [
        {
            "role": "user",
            "content": "Check this payload.",
        }
    ]
    assert captured["payload"]["temperature"] == 0.2
    assert captured["payload"]["max_tokens"] == 128
    assert captured["headers"]["Authorization"] == "Bearer test-api-key"
    assert captured["headers"]["Content-Type"] == "application/json"
    assert "test-api-key" not in response

    print("Fake transport payload/header smoke test passed.")


def test_empty_prompt_raises() -> None:
    config = OpenAICompatibleConfig.from_sources(env=valid_config_source())
    adapter = OpenAICompatibleAdapter(
        config,
        request_fn=lambda payload, headers: {
            "choices": [{"message": {"content": "Should not be used."}}]
        },
    )

    message = assert_raises_model_adapter_error(lambda: adapter.generate_response("  "))

    assert "empty prompt" in message
    print("Empty prompt smoke test passed.")


def test_malformed_fake_response_raises() -> None:
    config = OpenAICompatibleConfig.from_sources(env=valid_config_source())
    adapter = OpenAICompatibleAdapter(
        config,
        request_fn=lambda payload, headers: {"choices": [{"message": {"content": ""}}]},
    )

    message = assert_raises_model_adapter_error(
        lambda: adapter.generate_response("Prompt for malformed response.")
    )

    assert "content is empty or invalid" in message

    missing_choices_adapter = OpenAICompatibleAdapter(
        config,
        request_fn=lambda payload, headers: {"not_choices": []},
    )
    missing_choices_message = assert_raises_model_adapter_error(
        lambda: missing_choices_adapter.generate_response("Prompt for missing choices.")
    )

    assert "missing choices" in missing_choices_message
    print("Malformed fake response smoke test passed.")


def test_transport_exception_is_wrapped() -> None:
    config = OpenAICompatibleConfig.from_sources(env=valid_config_source())

    def failing_transport(payload, headers):
        raise RuntimeError("simulated failure with no secret")

    adapter = OpenAICompatibleAdapter(config, request_fn=failing_transport)
    message = assert_raises_model_adapter_error(
        lambda: adapter.generate_response("Prompt for transport failure.")
    )

    assert "transport failed" in message
    assert "RuntimeError" in message
    assert "test-api-key" not in message

    print("Transport exception wrapping smoke test passed.")


class FakeHTTPResponse:
    def __init__(self, body: bytes) -> None:
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None

    def read(self) -> bytes:
        return self.body


def test_http_helper_uses_urllib_shape_without_network() -> None:
    config = OpenAICompatibleConfig.from_sources(env=valid_config_source())
    adapter = OpenAICompatibleAdapter(config)
    payload = adapter.build_request_payload("HTTP helper prompt.")
    headers = adapter.build_request_headers()
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["data"] = request.data
        captured["authorization"] = request.get_header("Authorization")
        captured["content_type"] = request.get_header("Content-type")
        captured["timeout"] = timeout
        return FakeHTTPResponse(
            b'{"choices": [{"message": {"content": "HTTP helper response."}}]}'
        )

    response_data = openai_compatible_http_request(
        payload,
        headers,
        config,
        urlopen_fn=fake_urlopen,
    )

    assert captured["url"] == "https://example.test/v1"
    assert captured["authorization"] == "Bearer test-api-key"
    assert captured["content_type"] == "application/json"
    assert captured["timeout"] == 10.0
    assert b"HTTP helper prompt." in captured["data"]
    assert response_data["choices"][0]["message"]["content"] == "HTTP helper response."

    parsed_response = adapter.parse_response(response_data)

    assert parsed_response == "HTTP helper response."
    assert "test-api-key" not in parsed_response
    print("HTTP helper fake urllib smoke test passed.")


def test_http_helper_wraps_bad_json_without_network() -> None:
    config = OpenAICompatibleConfig.from_sources(env=valid_config_source())
    adapter = OpenAICompatibleAdapter(config)

    def fake_urlopen(request, timeout):
        return FakeHTTPResponse(b"not-json")

    message = assert_raises_model_adapter_error(
        lambda: openai_compatible_http_request(
            adapter.build_request_payload("Bad JSON prompt."),
            adapter.build_request_headers(),
            config,
            urlopen_fn=fake_urlopen,
        )
    )

    assert "not valid JSON" in message
    assert "test-api-key" not in message
    print("HTTP helper bad JSON wrapping smoke test passed.")


def test_manual_paste_remains_default() -> None:
    options = get_adapter_options()
    manual_options = [
        option
        for option in options
        if option["name"] == "Manual Paste"
    ]

    assert len(manual_options) == 1
    assert manual_options[0]["available"] is True
    assert manual_options[0]["default"] is True

    active_defaults = [
        option
        for option in options
        if option.get("default")
    ]
    assert active_defaults == manual_options

    print("Manual Paste default smoke test passed.")


def test_existing_mock_adapter_behavior() -> None:
    adapter = MockModelAdapter(
        responses_by_id={"CASE-001": "Mock response."},
        default_response="",
    )
    responses = generate_responses_for_cases(
        adapter,
        [
            {"id": "CASE-001", "prompt": "Prompt one"},
            {"id": "CASE-002", "prompt": "Prompt two"},
        ],
    )

    assert responses == {"CASE-001": "Mock response."}
    print("Existing MockModelAdapter behavior smoke test passed.")


def main() -> None:
    test_missing_api_key_raises()
    test_missing_model_raises()
    test_valid_config_without_network_call()
    test_adapter_does_not_make_real_api_calls()
    test_fake_transport_returns_response_text()
    test_fake_transport_receives_expected_payload_and_headers()
    test_empty_prompt_raises()
    test_malformed_fake_response_raises()
    test_transport_exception_is_wrapped()
    test_http_helper_uses_urllib_shape_without_network()
    test_http_helper_wraps_bad_json_without_network()
    test_manual_paste_remains_default()
    test_existing_mock_adapter_behavior()
    print("v0.8 adapter configuration smoke test passed.")


if __name__ == "__main__":
    main()
