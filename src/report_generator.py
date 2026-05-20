from __future__ import annotations

from datetime import datetime
from typing import Any, Dict


def generate_markdown_report(result: Dict[str, Any]) -> str:
    """Generate a Markdown report for a single LLM ShieldBench evaluation."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    strengths = "\n".join(f"- {item}" for item in result.get("strengths", []))
    issues = "\n".join(f"- {item}" for item in result.get("issues", []))

    return f"""# LLM ShieldBench Report

Generated: {timestamp}

## Summary

| Field | Value |
|---|---|
| Category | {result.get("category", "")} |
| Trust Score | {result.get("score", "")} / 100 |
| Risk Level | {result.get("risk_level", "")} |

## Original Prompt

```text
{result.get("prompt", "")}
```

## Chatbot Response

```text
{result.get("response", "")}
```

## Expected Safe Behavior

```text
{result.get("expected_behavior", "")}
```

## Strengths

{strengths}

## Issues

{issues}

## Recommendation

{result.get("recommendation", "")}

---

Built with **LLM ShieldBench** by **Vedansh Labs**.  
Building human-centered AI from research to reality.
"""


def generate_benchmark_markdown_report(benchmark_result: Dict[str, Any]) -> str:
    """Generate a Markdown report for Benchmark Mode results."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    category_lines = []
    for category, score in benchmark_result.get("category_scores", {}).items():
        category_lines.append(f"| {category} | {score} / 100 |")

    if not category_lines:
        category_lines.append("| N/A | N/A |")

    result_lines = []
    for item in benchmark_result.get("results", []):
        result_lines.append(
            f"| {item.get('id', '')} | {item.get('category', '')} | "
            f"{item.get('score', '')} / 100 | {item.get('risk_level', '')} |"
        )

    if not result_lines:
        result_lines.append("| N/A | N/A | N/A | N/A |")

    detailed_sections = []
    for item in benchmark_result.get("results", []):
        strengths = "\n".join(f"- {x}" for x in item.get("strengths", []))
        issues = "\n".join(f"- {x}" for x in item.get("issues", []))

        detailed_sections.append(
            f"""## Test Case: {item.get("id", "")} — {item.get("title", "")}

**Category:** {item.get("category", "")}  
**Score:** {item.get("score", "")} / 100  
**Risk Level:** {item.get("risk_level", "")}

### Prompt

```text
{item.get("prompt", "")}
```

### Chatbot Response

```text
{item.get("response", "")}
```

### Expected Safe Behavior

```text
{item.get("expected_behavior", "")}
```

### Strengths

{strengths}

### Issues

{issues}

### Recommendation

{item.get("recommendation", "")}
"""
        )

    details = "\n\n".join(detailed_sections)

    return f"""# LLM ShieldBench Benchmark Report

Generated: {timestamp}

## Benchmark Summary

| Field | Value |
|---|---|
| Overall Trust Score | {benchmark_result.get("overall_score", 0)} / 100 |
| Completed Test Cases | {benchmark_result.get("completed_cases", 0)} |
| Weakest Category | {benchmark_result.get("weakest_category", "N/A")} |

## Category Scores

| Category | Average Score |
|---|---|
{chr(10).join(category_lines)}

## Test Case Results

| ID | Category | Score | Risk Level |
|---|---|---|---|
{chr(10).join(result_lines)}

{details}

---

Built with **LLM ShieldBench** by **Vedansh Labs**.  
Building human-centered AI from research to reality.
"""
