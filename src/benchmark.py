from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from src.evaluator import run_single_evaluation


def load_benchmark_cases(path: str | Path = "data/test_cases.json") -> List[Dict[str, Any]]:
    file_path = Path(path)

    if not file_path.exists():
        return []

    return json.loads(file_path.read_text(encoding="utf-8"))


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