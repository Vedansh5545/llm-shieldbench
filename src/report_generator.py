from __future__ import annotations

from datetime import datetime
from typing import Any, Dict


def list_to_markdown(items: list[str]) -> str:
    cleaned_items = [item for item in items if item]

    if not cleaned_items:
        return "- None"

    return "\n".join(f"- {item}" for item in cleaned_items)




def markdown_table_value(value: Any) -> str:
    """Keep Markdown tables readable when values contain pipes or newlines."""
    text = str(value if value is not None else "")
    text = text.replace("|", "\\|")
    text = " ".join(text.splitlines())
    return text.strip()


def score_interpretation(score: Any) -> str:
    try:
        numeric_score = float(score)
    except (TypeError, ValueError):
        numeric_score = 0

    if numeric_score >= 85:
        return "Strong"
    if numeric_score >= 70:
        return "Good but watch"
    if numeric_score >= 50:
        return "Needs review"
    return "Weak / high concern"


def distribution_table_lines(
    counts: Dict[str, Any],
    ordered_labels: list[str],
    empty_label: str = "N/A",
) -> list[str]:
    if not counts:
        return [f"| {empty_label} | 0 |"]

    labels = [label for label in ordered_labels if label in counts]
    labels.extend(label for label in counts if label not in labels)

    return [
        f"| {markdown_table_value(label)} | {markdown_table_value(counts.get(label, 0))} |"
        for label in labels
    ]


def summarize_history_scores(history: list[Dict[str, Any]]) -> Dict[str, Any]:
    scores = []

    for item in history:
        try:
            scores.append(float(item.get("score", 0)))
        except (TypeError, ValueError):
            continue

    risk_counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}

    for item in history:
        risk_level = str(item.get("risk_level", "")).strip()

        if risk_level in risk_counts:
            risk_counts[risk_level] += 1

    return {
        "total_results": len(history),
        "average_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "low_risk": risk_counts["Low"],
        "medium_risk": risk_counts["Medium"],
        "high_risk": risk_counts["High"],
        "critical_risk": risk_counts["Critical"],
        "most_recent": history[-1].get("timestamp", "N/A") if history else "N/A",
    }


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
        category_lines.append(
            f"| {markdown_table_value(category)} | {markdown_table_value(score)} / 100 | "
            f"{markdown_table_value(score_interpretation(score))} |"
        )

    if not category_lines:
        category_lines.append("| N/A | N/A | N/A |")

    risk_lines = distribution_table_lines(
        benchmark_result.get("risk_counts", {}),
        ["Low", "Medium", "High", "Critical"],
    )

    severity_lines = []

    for severity, count in benchmark_result.get("severity_counts", {}).items():
        severity_lines.append(
            f"| {markdown_table_value(severity)} | {markdown_table_value(count)} |"
        )

    if not severity_lines:
        severity_lines.append("| N/A | N/A |")

    failure_label_lines = []

    for label, count in benchmark_result.get("failure_label_counts", {}).items():
        failure_label_lines.append(
            f"| {markdown_table_value(label)} | {markdown_table_value(count)} |"
        )

    if not failure_label_lines:
        failure_label_lines.append("| None | 0 |")

    weakest_category = benchmark_result.get("weakest_category", "N/A")
    category_scores = benchmark_result.get("category_scores", {})
    weakest_score = category_scores.get(weakest_category)

    if weakest_category == "N/A" or weakest_score is None:
        weakest_explanation = (
            "No weakest category is available yet. Run benchmark cases to generate "
            "category analytics."
        )
    else:
        weakest_explanation = (
            f"The weakest category is {weakest_category} with an average trust score "
            f"of {weakest_score}. This means responses in this area may need closer review."
        )

    result_lines = []

    for item in benchmark_result.get("results", []):
        labels = ", ".join(item.get("failure_labels", ["None"]))

        result_lines.append(
            f"| {markdown_table_value(item.get('id', ''))} | "
            f"{markdown_table_value(item.get('category', ''))} | "
            f"{markdown_table_value(item.get('score', ''))} / 100 | "
            f"{markdown_table_value(item.get('risk_level', ''))} | "
            f"{markdown_table_value(item.get('severity', 'N/A'))} | "
            f"{markdown_table_value(labels)} |"
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
| Weakest Category | {markdown_table_value(weakest_category)} |

## Score Interpretation

| Score Range | Meaning |
|---|---|
| 85-100 | Strong |
| 70-84 | Good but watch |
| 50-69 | Needs review |
| Below 50 | Weak / high concern |

## Category Summary

| Category | Average Score | Interpretation |
|---|---|---|
{chr(10).join(category_lines)}

## Weakest-category Explanation

{weakest_explanation}

## Risk Distribution

| Risk Level | Count |
|---|---|
{chr(10).join(risk_lines)}

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


def generate_history_markdown_report(history: list[Dict[str, Any]]) -> str:
    """Generate a Markdown export for v0.5 session-based evaluation history."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    summary = summarize_history_scores(history)

    if not history:
        return f"""# LLM ShieldBench Evaluation History

Generated: {timestamp}

No evaluation history is currently stored in this session.

---

Built with **LLM ShieldBench** by **Vedansh Labs**.  
Building human-centered AI from research to reality.
"""

    risk_summary = f"""| Risk Level | Count |
|---|---|
| Low | {summary["low_risk"]} |
| Medium | {summary["medium_risk"]} |
| High | {summary["high_risk"]} |
| Critical | {summary["critical_risk"]} |"""

    result_lines = []

    for item in history:
        labels = ", ".join(item.get("failure_labels", ["None"]))

        result_lines.append(
            f"| {markdown_table_value(item.get('timestamp', ''))} | "
            f"{markdown_table_value(item.get('mode', ''))} | "
            f"{markdown_table_value(item.get('case_id', ''))} | "
            f"{markdown_table_value(item.get('category', ''))} | "
            f"{markdown_table_value(item.get('score', 0))} / 100 | "
            f"{markdown_table_value(item.get('risk_level', ''))} | "
            f"{markdown_table_value(item.get('severity', ''))} | "
            f"{markdown_table_value(labels)} |"
        )

    detailed_sections = []

    for index, item in enumerate(history, start=1):
        strengths = list_to_markdown(item.get("strengths", []))
        issues = list_to_markdown(item.get("issues", []))
        failure_labels = list_to_markdown(item.get("failure_labels", ["None"]))

        case_id = item.get("case_id", "")
        title = item.get("title", "")
        mode = item.get("mode", "")
        category = item.get("category", "")

        if case_id or title:
            case_label = f"{case_id} — {title}".strip(" —")
        else:
            case_label = f"{mode} — {category}".strip(" —") or f"History Item {index}"

        detailed_sections.append(
            f"""## History Item {index}: {case_label}

**Timestamp:** {item.get("timestamp", "")}  
**Mode:** {item.get("mode", "")}  
**Run ID:** {item.get("run_id", "")}  
**Category:** {item.get("category", "")}  
**Score:** {item.get("score", 0)} / 100  
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

    return f"""# LLM ShieldBench Evaluation History

Generated: {timestamp}

## Session Summary

| Field | Value |
|---|---|
| Stored Results | {summary["total_results"]} |
| Average Trust Score | {summary["average_score"]} / 100 |
| Most Recent Run | {summary["most_recent"]} |

## Risk Summary

{risk_summary}

## History Table

| Timestamp | Mode | Case ID | Category | Score | Risk Level | Severity | Failure Labels |
|---|---|---|---|---|---|---|---|
{chr(10).join(result_lines)}

{chr(10).join(detailed_sections)}

---

Built with **LLM ShieldBench** by **Vedansh Labs**.  
Building human-centered AI from research to reality.
"""
