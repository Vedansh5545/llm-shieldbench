from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .scoring import evaluate_response


def load_test_cases(path: str | Path = "data/test_cases.json") -> List[Dict[str, Any]]:
    file_path = Path(path)
    if not file_path.exists():
        return []
    return json.loads(file_path.read_text(encoding="utf-8"))


def run_single_evaluation(category: str, prompt: str, response: str, expected_behavior: str = "") -> Dict[str, Any]:
    result = evaluate_response(category, prompt, response, expected_behavior)
    return {
        "category": category,
        "prompt": prompt,
        "response": response,
        "expected_behavior": expected_behavior,
        "score": result.score,
        "risk_level": result.risk_level,
        "strengths": result.strengths,
        "issues": result.issues,
        "recommendation": result.recommendation,
    }
