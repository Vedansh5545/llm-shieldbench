"""Provider-neutral model adapter foundation for v0.7.

This module is architecture-only. It does not make real API calls, load API
keys, or include provider-specific logic for OpenAI, Ollama, Anthropic, or any
other model provider.

Manual paste remains the default workflow for v0.7. The adapter classes here
exist so future versions can add real model integrations behind a small,
consistent interface.
"""

from __future__ import annotations


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
    ]
