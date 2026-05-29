"""Provider-neutral model adapter foundation for v0.7.

This module is architecture-only. It does not make real API calls, load API
keys, or include provider-specific logic for OpenAI, Ollama, Anthropic, or any
other model provider.

Manual paste remains the default workflow for v0.7. The adapter classes here
exist so future versions can add real model integrations behind a small,
consistent interface.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass


API_KEY_ENV_NAME = "LLM_SHIELDBENCH_API_KEY"
BASE_URL_ENV_NAME = "LLM_SHIELDBENCH_BASE_URL"
MODEL_ENV_NAME = "LLM_SHIELDBENCH_MODEL"
TIMEOUT_SECONDS_ENV_NAME = "LLM_SHIELDBENCH_TIMEOUT_SECONDS"
MAX_TOKENS_ENV_NAME = "LLM_SHIELDBENCH_MAX_TOKENS"
TEMPERATURE_ENV_NAME = "LLM_SHIELDBENCH_TEMPERATURE"


class ModelAdapterError(Exception):
    """Raised when a model adapter cannot generate a response."""


class ModelAdapter:
    """Lightweight base class for future model adapters.

    v0.7 is architecture-only, so subclasses in this module are safe
    placeholders or deterministic helpers. No real API calls are made here.
    """

    name: str = "Model Adapter"
    enabled: bool = False

    def generate_response(self, prompt: str, *, case: dict | None = None) -> str:
        """Return a response for a prompt.

        Real provider-backed implementations can override this method in a
        future version.
        """
        raise ModelAdapterError("ModelAdapter does not implement response generation.")


class ManualPasteAdapter(ModelAdapter):
    """Adapter representing the current manual paste workflow.

    Manual paste remains the default workflow. This adapter is enabled for UI
    selection, but it intentionally does not generate responses.
    """

    name = "Manual Paste"
    enabled = True

    def generate_response(self, prompt: str, *, case: dict | None = None) -> str:
        """Raise because manual paste responses come from the UI."""
        raise ModelAdapterError(
            "ManualPasteAdapter does not generate responses. "
            "Use pasted responses from the UI."
        )


class DisabledModelAdapter(ModelAdapter):
    """Safe placeholder for unavailable model adapters.

    This keeps v0.7 provider-neutral. No real API calls are made.
    """

    name = "Disabled Model Adapter"
    enabled = False

    def generate_response(self, prompt: str, *, case: dict | None = None) -> str:
        """Raise because this adapter is intentionally disabled."""
        raise ModelAdapterError(
            "Model adapter is disabled. Configure a real adapter in a future version."
        )


class MockModelAdapter(ModelAdapter):
    """Deterministic test adapter with no external dependencies.

    Responses can be mapped by test case ID. If no mapped response exists, the
    adapter returns the configured default response.
    """

    name = "Mock Model Adapter"
    enabled = True

    def __init__(
        self,
        responses_by_id: dict[str, str] | None = None,
        default_response: str = "",
    ) -> None:
        self.responses_by_id = responses_by_id or {}
        self.default_response = default_response

    def generate_response(self, prompt: str, *, case: dict | None = None) -> str:
        """Return a deterministic response for the given case."""
        if case is not None:
            case_id = case.get("id")
            if case_id in self.responses_by_id:
                return self.responses_by_id[case_id]

        return self.default_response


@dataclass(repr=False)
class OpenAICompatibleConfig:
    """Safe configuration for a future OpenAI-compatible adapter.

    v0.8 Checkpoint 1 is configuration-only. This object validates settings for
    a future OpenAI-compatible request path, but it does not make API calls and
    does not expose secrets in its string representation.
    """

    api_key: str
    base_url: str
    model: str
    timeout_seconds: float = 30.0
    max_tokens: int = 512
    temperature: float = 0.0

    @classmethod
    def from_sources(
        cls,
        env: dict[str, object] | None = None,
        secrets: dict[str, object] | None = None,
    ) -> "OpenAICompatibleConfig":
        """Create config from env-style and secrets-style mappings.

        Passed dictionaries are preferred for tests. If no env mapping is
        provided, the process environment is used. Secret values are never
        printed, logged, or stored outside this object.
        """
        env_source = os.environ if env is None else env
        secrets_source = secrets or {}

        api_key = _read_config_value(API_KEY_ENV_NAME, env_source, secrets_source)
        base_url = _read_config_value(BASE_URL_ENV_NAME, env_source, secrets_source)
        model = _read_config_value(MODEL_ENV_NAME, env_source, secrets_source)
        timeout_seconds = _read_config_value(
            TIMEOUT_SECONDS_ENV_NAME,
            env_source,
            secrets_source,
            default="30",
        )
        max_tokens = _read_config_value(
            MAX_TOKENS_ENV_NAME,
            env_source,
            secrets_source,
            default="512",
        )
        temperature = _read_config_value(
            TEMPERATURE_ENV_NAME,
            env_source,
            secrets_source,
            default="0",
        )

        return cls(
            api_key=str(api_key or "").strip(),
            base_url=str(base_url or "").strip(),
            model=str(model or "").strip(),
            timeout_seconds=_parse_positive_float(
                timeout_seconds,
                "timeout_seconds",
            ),
            max_tokens=_parse_positive_int(max_tokens, "max_tokens"),
            temperature=_parse_temperature(temperature),
        ).validate()

    def validate(self) -> "OpenAICompatibleConfig":
        """Validate required fields and numeric options."""
        if not self.api_key:
            raise ModelAdapterError("OpenAI-compatible adapter is missing an API key.")

        if not self.base_url:
            raise ModelAdapterError("OpenAI-compatible adapter is missing a base URL.")

        if not self.model:
            raise ModelAdapterError("OpenAI-compatible adapter is missing a model.")

        if self.timeout_seconds <= 0:
            raise ModelAdapterError("timeout_seconds must be greater than 0.")

        if self.max_tokens <= 0:
            raise ModelAdapterError("max_tokens must be greater than 0.")

        if self.temperature < 0:
            raise ModelAdapterError("temperature must be 0 or greater.")

        return self

    def __repr__(self) -> str:
        return (
            "OpenAICompatibleConfig("
            "api_key=<redacted>, "
            f"base_url={self.base_url!r}, "
            f"model={self.model!r}, "
            f"timeout_seconds={self.timeout_seconds!r}, "
            f"max_tokens={self.max_tokens!r}, "
            f"temperature={self.temperature!r})"
        )


class OpenAICompatibleAdapter(ModelAdapter):
    """Fake-transport OpenAI-compatible adapter placeholder for v0.8.

    Real API execution is intentionally not enabled by default. Tests may inject
    a fake request function to verify request-building and response-parsing
    behavior without making network calls.
    """

    name = "OpenAI-Compatible Adapter"
    enabled = False

    def __init__(self, config: OpenAICompatibleConfig, request_fn=None) -> None:
        self.config = config.validate()
        self.request_fn = request_fn

    def generate_response(self, prompt: str, *, case: dict | None = None) -> str:
        """Generate a response only through an injected fake request function."""
        clean_prompt = str(prompt or "").strip()

        if not clean_prompt:
            raise ModelAdapterError("OpenAI-compatible adapter received an empty prompt.")

        if self.request_fn is None:
            raise ModelAdapterError(
                "OpenAI-compatible API execution is not enabled or configured yet."
            )

        payload = self.build_request_payload(clean_prompt)
        headers = self.build_request_headers()

        try:
            response_data = self.request_fn(payload, headers)
        except ModelAdapterError:
            raise
        except Exception as exc:
            raise ModelAdapterError(
                f"OpenAI-compatible transport failed: {exc.__class__.__name__}."
            ) from exc

        return self.parse_response(response_data)

    def build_request_payload(self, prompt: str) -> dict:
        """Build an OpenAI-compatible chat completions request payload."""
        return {
            "model": self.config.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

    def build_request_headers(self) -> dict[str, str]:
        """Build headers without exposing them in logs or UI."""
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

    def parse_response(self, response_data: object) -> str:
        """Parse a fake OpenAI-compatible response dictionary."""
        if not isinstance(response_data, dict):
            raise ModelAdapterError("OpenAI-compatible response is malformed.")

        choices = response_data.get("choices")

        if not choices:
            raise ModelAdapterError("OpenAI-compatible response is missing choices.")

        if not isinstance(choices, list):
            raise ModelAdapterError("OpenAI-compatible response choices are malformed.")

        first_choice = choices[0]

        if not isinstance(first_choice, dict):
            raise ModelAdapterError("OpenAI-compatible response choice is malformed.")

        message = first_choice.get("message")

        if not isinstance(message, dict):
            raise ModelAdapterError("OpenAI-compatible response message is malformed.")

        content = message.get("content")

        if not isinstance(content, str) or not content.strip():
            raise ModelAdapterError(
                "OpenAI-compatible response content is empty or invalid."
            )

        return content.strip()


def _read_config_value(
    key: str,
    env: dict[str, object],
    secrets: dict[str, object],
    default: object = "",
) -> object:
    if key in secrets:
        return secrets[key]

    return env.get(key, default)


def _parse_positive_float(value: object, field_name: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        raise ModelAdapterError(f"{field_name} must be a valid number.") from None

    if parsed <= 0:
        raise ModelAdapterError(f"{field_name} must be greater than 0.")

    return parsed


def _parse_positive_int(value: object, field_name: str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ModelAdapterError(f"{field_name} must be a valid integer.") from None

    if parsed <= 0:
        raise ModelAdapterError(f"{field_name} must be greater than 0.")

    return parsed


def _parse_temperature(value: object) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        raise ModelAdapterError("temperature must be a valid number.") from None

    if parsed < 0:
        raise ModelAdapterError("temperature must be 0 or greater.")

    return parsed


def openai_compatible_http_request(
    payload: dict,
    headers: dict[str, str],
    config: OpenAICompatibleConfig,
    urlopen_fn=None,
) -> dict:
    """Send one OpenAI-compatible chat request using the standard library.

    This helper is only used when the caller explicitly injects it into an
    adapter. It never prints headers or secrets.
    """
    opener = urllib.request.urlopen if urlopen_fn is None else urlopen_fn

    try:
        request = urllib.request.Request(
            config.base_url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with opener(request, timeout=config.timeout_seconds) as response:
            raw_body = response.read().decode("utf-8")

        parsed = json.loads(raw_body)

    except urllib.error.HTTPError as exc:
        raise ModelAdapterError(
            f"OpenAI-compatible HTTP request failed with status {exc.code}."
        ) from exc

    except urllib.error.URLError as exc:
        raise ModelAdapterError(
            f"OpenAI-compatible HTTP request failed: {exc.reason}."
        ) from exc

    except TimeoutError as exc:
        raise ModelAdapterError("OpenAI-compatible HTTP request timed out.") from exc

    except json.JSONDecodeError as exc:
        raise ModelAdapterError(
            "OpenAI-compatible HTTP response was not valid JSON."
        ) from exc

    except OSError as exc:
        raise ModelAdapterError(
            f"OpenAI-compatible HTTP request failed: {exc.__class__.__name__}."
        ) from exc

    if not isinstance(parsed, dict):
        raise ModelAdapterError("OpenAI-compatible HTTP response JSON is malformed.")

    return parsed


def generate_responses_for_cases(
    adapter: ModelAdapter,
    test_cases: list[dict],
) -> dict[str, str]:
    """Generate responses for test cases using a provider-neutral adapter.

    v0.7 remains architecture-only. This helper only calls the provided adapter
    interface and skips cases that do not have enough data for a safe response.
    """
    if not adapter.enabled:
        raise ModelAdapterError(
            "Model adapter is disabled. Configure a real adapter in a future version."
        )

    responses: dict[str, str] = {}

    for case in test_cases:
        case_id = case.get("id")
        prompt = case.get("prompt")

        if not case_id or not prompt:
            continue

        response = adapter.generate_response(prompt, case=case).strip()
        if not response:
            continue

        responses[str(case_id)] = response

    return responses


def get_adapter_options() -> list[dict]:
    """Return adapter metadata without configuring real model providers.

    Manual paste remains the default workflow. The other entries are safe
    placeholders for unavailable or testing-only adapters.
    """
    return [
        {
            "id": "manual_paste",
            "name": "Manual Paste",
            "available": True,
            "default": True,
            "description": "Default workflow using responses pasted from the UI.",
        },
        {
            "id": "disabled",
            "name": "Disabled Model Adapter",
            "available": False,
            "default": False,
            "description": "Unavailable placeholder for future real adapters.",
        },
        {
            "id": "mock",
            "name": "Mock Model Adapter",
            "available": True,
            "default": False,
            "description": "Testing-only deterministic adapter with no external calls.",
        },
        {
            "id": "openai_compatible",
            "name": "OpenAI-Compatible Adapter",
            "available": False,
            "default": False,
            "description": (
                "Configuration-only v0.8 placeholder. Real API execution is not enabled."
            ),
        },
    ]
