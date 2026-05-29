from __future__ import annotations

import sys
from pathlib import Path

# Allow running this script from the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.model_adapters import (
    DisabledModelAdapter,
    ManualPasteAdapter,
    MockModelAdapter,
    ModelAdapterError,
    generate_responses_for_cases,
    get_adapter_options,
)


def assert_raises_model_adapter_error(callable_to_test) -> None:
    try:
        callable_to_test()
    except ModelAdapterError:
        return

    raise AssertionError("Expected ModelAdapterError to be raised.")


def test_manual_paste_adapter() -> None:
    adapter = ManualPasteAdapter()

    assert adapter.enabled is True
    assert adapter.name == "Manual Paste"
    assert_raises_model_adapter_error(
        lambda: adapter.generate_response("Test prompt", case={"id": "CASE-001"})
    )

    print("ManualPasteAdapter smoke test passed.")


def test_disabled_model_adapter() -> None:
    adapter = DisabledModelAdapter()

    assert adapter.enabled is False
    assert_raises_model_adapter_error(
        lambda: adapter.generate_response("Test prompt", case={"id": "CASE-001"})
    )
    assert_raises_model_adapter_error(
        lambda: generate_responses_for_cases(
            adapter,
            [{"id": "CASE-001", "prompt": "Prompt one"}],
        )
    )

    print("DisabledModelAdapter smoke test passed.")


def test_mock_model_adapter_mapped_responses() -> None:
    test_cases = [
        {"id": "CASE-001", "prompt": "Prompt one"},
        {"id": "CASE-002", "prompt": "Prompt two"},
        {"id": "CASE-003", "prompt": "Prompt three"},
    ]
    adapter = MockModelAdapter(
        responses_by_id={
            "CASE-001": "Response one.",
            "CASE-002": "Response two.",
        }
    )

    responses = generate_responses_for_cases(adapter, test_cases)

    assert responses == {
        "CASE-001": "Response one.",
        "CASE-002": "Response two.",
    }
    assert "CASE-003" not in responses

    print("MockModelAdapter mapped response smoke test passed.")


def test_mock_model_adapter_default_response() -> None:
    test_cases = [
        {"id": "CASE-001", "prompt": "Prompt one"},
        {"id": "CASE-002", "prompt": "Prompt two"},
    ]
    adapter = MockModelAdapter(default_response="Default mock response.")

    responses = generate_responses_for_cases(adapter, test_cases)

    assert responses == {
        "CASE-001": "Default mock response.",
        "CASE-002": "Default mock response.",
    }

    print("MockModelAdapter default response smoke test passed.")


def test_adapter_options() -> None:
    options = get_adapter_options()
    option_names = {option["name"] for option in options}

    assert isinstance(options, list)
    assert len(options) > 0
    assert "Manual Paste" in option_names
    assert "Disabled Model Adapter" in option_names
    assert "Mock Model Adapter" in option_names

    print("Adapter options smoke test passed.")


def main() -> None:
    test_manual_paste_adapter()
    test_disabled_model_adapter()
    test_mock_model_adapter_mapped_responses()
    test_mock_model_adapter_default_response()
    test_adapter_options()
    print("v0.7 adapter smoke test passed.")


if __name__ == "__main__":
    main()
