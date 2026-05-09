from __future__ import annotations

from datetime import datetime
from typing import Any, Dict


def generate_markdown_report(result: Dict[str, Any]) -> str:
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
