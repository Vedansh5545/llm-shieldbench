from __future__ import annotations

from datetime import datetime
from typing import Any, Dict


def list_to_markdown(items: list[str]) -> str:
    cleaned_items = [item for item in items if item]

    if not cleaned_items:
        return "- None"

    return "\n".join(f"- {item}" for item in cleaned_items)


def generate_markdown_report(result: Dict[str, Any]) -> str:
    """Generate a Markdown report for a single LLM ShieldBench evaluation."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    strengths = list_to_markdown(result.get("strengths", []))
    issues = list_to_markdown(result.get("issues", []))
    failure_labels = list_to_markdown(result.get("failure_labels", ["None"]))

    return f"""# LLM ShieldBench Report

Generated: {timestamp}

## Summary

| Field | Value |
|---|---|
| Category | {result.get("category", "")} |
| Trust Score | {result.get("score", "")} / 100 |
| Risk Level | {result.get("risk_level", "")} |
| Severity | {result.get("severity", "N/A")} |

## Failure Labels

{failure_labels}

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

    severity_lines = []

    for severity, count in benchmark_result.get("severity_counts", {}).items():
        severity_lines.append(f"| {severity} | {count} |")

    if not severity_lines:
        severity_lines.append("| N/A | N/A |")

    failure_label_lines = []

    for label, count in benchmark_result.get("failure_label_counts", {}).items():
        failure_label_lines.append(f"| {label} | {count} |")

    if not failure_label_lines:
        failure_label_lines.append("| None | 0 |")

    result_lines = []

    for item in benchmark_result.get("results", []):
        labels = ", ".join(item.get("failure_labels", ["None"]))

        result_lines.append(
            f"| {item.get('id', '')} | {item.get('category', '')} | "
            f"{item.get('score', '')} / 100 | {item.get('risk_level', '')} | "
            f"{item.get('severity', 'N/A')} | {labels} |"
        )

    if not result_lines:
        result_lines.append("| N/A | N/A | N/A | N/A | N/A | N/A |")

    detailed_sections = []

    for item in benchmark_result.get("results", []):
        strengths = list_to_markdown(item.get("strengths", []))
        issues = list_to_markdown(item.get("issues", []))
        failure_labels = list_to_markdown(item.get("failure_labels", ["None"]))

        detailed_sections.append(
            f"""## Test Case: {item.get("id", "")} — {item.get("title", "")}

**Category:** {item.get("category", "")}  
**Score:** {item.get("score", "")} / 100  
**Risk Level:** {item.get("risk_level", "")}  
**Severity:** {item.get("severity", "N/A")}

### Failure Labels

{failure_labels}

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

## Severity Distribution

| Severity | Count |
|---|---|
{chr(10).join(severity_lines)}

## Failure Label Counts

| Failure Label | Count |
|---|---|
{chr(10).join(failure_label_lines)}

## Test Case Results

| ID | Category | Score | Risk Level | Severity | Failure Labels |
|---|---|---|---|---|---|
{chr(10).join(result_lines)}

{details}

---

Built with **LLM ShieldBench** by **Vedansh Labs**.  
Building human-centered AI from research to reality.
"""