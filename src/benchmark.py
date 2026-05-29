from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from src.evaluator import run_single_evaluation
from src.model_adapters import ModelAdapter, generate_responses_for_cases


SUPPORTED_CATEGORIES = {
    "Prompt Injection",
    "Privacy Safety",
    "Hallucination Control",
    "Unsafe Advice Handling",
    "Instruction Following",
}

REQUIRED_CASE_FIELDS = {
    "id",
    "title",
    "category",
    "prompt",
    "expected_safe_behavior",
}

OPTIONAL_CASE_FIELDS = {
    "tags",
    "difficulty",
    "source",
    "notes",
}


def load_benchmark_cases(path: str | Path = "data/test_cases.json") -> List[Dict[str, Any]]:
    """
    Load built-in benchmark cases from disk.

    This keeps the old v0.2/v0.3 behavior unchanged:
    if the file does not exist, return an empty list.
    """
    file_path = Path(path)

    if not file_path.exists():
        return []

    return json.loads(file_path.read_text(encoding="utf-8"))


def read_json_payload(payload: Any) -> Tuple[Optional[Any], List[str]]:
    """
    Read JSON from a string, bytes object, pathlib path, or Streamlit uploaded file.

    Returns:
        parsed_json, errors
    """
    errors: List[str] = []

    try:
        if isinstance(payload, Path):
            raw_text = payload.read_text(encoding="utf-8")

        elif isinstance(payload, str):
            possible_path = Path(payload)

            if possible_path.exists() and possible_path.is_file():
                raw_text = possible_path.read_text(encoding="utf-8")
            else:
                raw_text = payload

        elif isinstance(payload, bytes):
            raw_text = payload.decode("utf-8")

        elif hasattr(payload, "getvalue"):
            raw_bytes = payload.getvalue()

            if isinstance(raw_bytes, bytes):
                raw_text = raw_bytes.decode("utf-8")
            else:
                raw_text = str(raw_bytes)

        elif hasattr(payload, "read"):
            raw_data = payload.read()

            if isinstance(raw_data, bytes):
                raw_text = raw_data.decode("utf-8")
            else:
                raw_text = str(raw_data)

        else:
            errors.append(
                "Unsupported input type. Provide a JSON string, bytes, path, or uploaded file."
            )
            return None, errors

        parsed = json.loads(raw_text)
        return parsed, errors

    except UnicodeDecodeError:
        errors.append("The uploaded file could not be decoded as UTF-8 text.")
        return None, errors

    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON: {exc.msg} at line {exc.lineno}, column {exc.colno}.")
        return None, errors

    except OSError as exc:
        errors.append(f"Could not read JSON file: {exc}")
        return None, errors


def normalize_string(value: Any) -> str:
    """Convert values to a clean string for benchmark case fields."""
    if value is None:
        return ""

    return str(value).strip()


def normalize_tags(value: Any) -> List[str]:
    """Normalize optional tags into a list of strings."""
    if value is None:
        return []

    if isinstance(value, list):
        return [normalize_string(item) for item in value if normalize_string(item)]

    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]

    return []


def normalize_benchmark_case(
    case: Dict[str, Any],
    index: int,
) -> Tuple[Optional[Dict[str, Any]], List[str], List[str]]:
    """
    Normalize and validate one benchmark case.

    Returns:
        normalized_case, errors, warnings
    """
    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(case, dict):
        return None, [f"Case #{index + 1} must be a JSON object."], warnings

    missing_fields = [
        field
        for field in REQUIRED_CASE_FIELDS
        if field not in case or normalize_string(case.get(field)) == ""
    ]

    if missing_fields:
        errors.append(
            f"Case #{index + 1} is missing required field(s): {', '.join(missing_fields)}."
        )
        return None, errors, warnings

    normalized_case: Dict[str, Any] = {
        "id": normalize_string(case.get("id")),
        "title": normalize_string(case.get("title")),
        "category": normalize_string(case.get("category")),
        "prompt": normalize_string(case.get("prompt")),
        "expected_safe_behavior": normalize_string(case.get("expected_safe_behavior")),
    }

    if normalized_case["category"] not in SUPPORTED_CATEGORIES:
        errors.append(
            f"Case {normalized_case['id']} has unsupported category "
            f"'{normalized_case['category']}'. Supported categories: "
            f"{', '.join(sorted(SUPPORTED_CATEGORIES))}."
        )

    if len(normalized_case["prompt"]) < 5:
        errors.append(f"Case {normalized_case['id']} has a prompt that is too short.")

    if len(normalized_case["expected_safe_behavior"]) < 5:
        errors.append(
            f"Case {normalized_case['id']} has expected_safe_behavior that is too short."
        )

    if len(normalized_case["prompt"]) > 8000:
        warnings.append(
            f"Case {normalized_case['id']} has a very long prompt. "
            "It will still run, but may make the UI harder to read."
        )

    if len(normalized_case["expected_safe_behavior"]) > 4000:
        warnings.append(
            f"Case {normalized_case['id']} has a very long expected_safe_behavior field."
        )

    normalized_case["tags"] = normalize_tags(case.get("tags"))
    normalized_case["difficulty"] = normalize_string(case.get("difficulty"))
    normalized_case["source"] = normalize_string(case.get("source"))
    normalized_case["notes"] = normalize_string(case.get("notes"))

    extra_fields = sorted(
        set(case.keys()).difference(REQUIRED_CASE_FIELDS).difference(OPTIONAL_CASE_FIELDS)
    )

    if extra_fields:
        warnings.append(
            f"Case {normalized_case['id']} contains extra field(s) that will be ignored: "
            f"{', '.join(extra_fields)}."
        )

    if errors:
        return None, errors, warnings

    return normalized_case, errors, warnings


def validate_benchmark_cases(payload: Any) -> Dict[str, Any]:
    """
    Validate a benchmark case payload.

    Expected format:
    [
      {
        "id": "CUSTOM-001",
        "title": "Custom test",
        "category": "Prompt Injection",
        "prompt": "...",
        "expected_safe_behavior": "..."
      }
    ]

    Returns a structured validation result:
    {
        "valid": bool,
        "cases": list,
        "errors": list,
        "warnings": list,
        "case_count": int
    }
    """
    errors: List[str] = []
    warnings: List[str] = []
    normalized_cases: List[Dict[str, Any]] = []

    if not isinstance(payload, list):
        return {
            "valid": False,
            "cases": [],
            "errors": ["Benchmark JSON must be a list of test case objects."],
            "warnings": [],
            "case_count": 0,
        }

    if not payload:
        return {
            "valid": False,
            "cases": [],
            "errors": ["Benchmark JSON cannot be empty. Add at least one test case."],
            "warnings": [],
            "case_count": 0,
        }

    seen_ids = set()

    for index, case in enumerate(payload):
        normalized_case, case_errors, case_warnings = normalize_benchmark_case(case, index)

        errors.extend(case_errors)
        warnings.extend(case_warnings)

        if normalized_case is None:
            continue

        case_id = normalized_case["id"]

        if case_id in seen_ids:
            errors.append(f"Duplicate case id found: {case_id}. Each case id must be unique.")
            continue

        seen_ids.add(case_id)
        normalized_cases.append(normalized_case)

    return {
        "valid": len(errors) == 0,
        "cases": normalized_cases if len(errors) == 0 else [],
        "errors": errors,
        "warnings": warnings,
        "case_count": len(normalized_cases),
    }


def load_custom_benchmark_cases(payload: Any) -> Dict[str, Any]:
    """
    Parse and validate custom benchmark cases from a JSON payload.

    Supports:
    - JSON string
    - bytes
    - pathlib Path
    - Streamlit uploaded file
    """
    parsed_json, parse_errors = read_json_payload(payload)

    if parse_errors:
        return {
            "valid": False,
            "cases": [],
            "errors": parse_errors,
            "warnings": [],
            "case_count": 0,
        }

    return validate_benchmark_cases(parsed_json)


def get_case_category_counts(test_cases: List[Dict[str, Any]]) -> Dict[str, int]:
    """Return category distribution for benchmark cases."""
    return dict(Counter(case.get("category", "Unknown") for case in test_cases))


def run_benchmark_from_responses(
    test_cases: List[Dict[str, Any]],
    responses_by_id: Dict[str, str],
) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []

    for case in test_cases:
        case_id = case["id"]
        response = responses_by_id.get(case_id, "").strip()

        if not response:
            continue

        result = run_single_evaluation(
            category=case["category"],
            prompt=case["prompt"],
            response=response,
            expected_behavior=case.get("expected_safe_behavior", ""),
        )

        result["id"] = case_id
        result["title"] = case.get("title", "")
        results.append(result)

    if not results:
        return {
            "overall_score": 0,
            "completed_cases": 0,
            "category_scores": {},
            "risk_counts": {},
            "severity_counts": {},
            "failure_label_counts": {},
            "weakest_category": "N/A",
            "results": [],
        }

    overall_score = round(sum(item["score"] for item in results) / len(results), 2)

    category_buckets: Dict[str, List[int]] = defaultdict(list)

    for item in results:
        category_buckets[item["category"]].append(item["score"])

    category_scores = {
        category: round(sum(scores) / len(scores), 2)
        for category, scores in category_buckets.items()
    }

    weakest_category = min(category_scores, key=category_scores.get)

    risk_counts = dict(Counter(item["risk_level"] for item in results))
    severity_counts = dict(Counter(item.get("severity", "Unknown") for item in results))

    failure_label_counter: Counter[str] = Counter()

    for item in results:
        for label in item.get("failure_labels", []):
            if label != "None":
                failure_label_counter[label] += 1

    return {
        "overall_score": overall_score,
        "completed_cases": len(results),
        "category_scores": category_scores,
        "risk_counts": risk_counts,
        "severity_counts": severity_counts,
        "failure_label_counts": dict(failure_label_counter),
        "weakest_category": weakest_category,
        "results": results,
    }


def run_benchmark_with_adapter(
    test_cases: List[Dict[str, Any]],
    adapter: ModelAdapter,
) -> Dict[str, Any]:
    """Run a benchmark using responses produced by a model adapter.

    v0.7 keeps this helper architecture-only. It does not call model providers
    directly; it only asks the provided adapter for responses and then reuses
    the existing manual-response benchmark scoring flow.
    """
    responses_by_id = generate_responses_for_cases(adapter, test_cases)
    return run_benchmark_from_responses(test_cases, responses_by_id)


def benchmark_to_dataframe(benchmark_result: Dict[str, Any]) -> pd.DataFrame:
    rows = []

    for item in benchmark_result.get("results", []):
        rows.append(
            {
                "ID": item.get("id", ""),
                "Title": item.get("title", ""),
                "Category": item.get("category", ""),
                "Score": item.get("score", ""),
                "Risk Level": item.get("risk_level", ""),
                "Severity": item.get("severity", ""),
                "Failure Labels": ", ".join(item.get("failure_labels", [])),
                "Recommendation": item.get("recommendation", ""),
            }
        )

    return pd.DataFrame(rows)
