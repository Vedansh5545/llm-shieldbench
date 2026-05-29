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
    test_manual_paste_remains_default()
    test_existing_mock_adapter_behavior()
    print("v0.8 adapter configuration smoke test passed.")


if __name__ == "__main__":
    main()
