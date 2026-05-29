# Contributing to LLM ShieldBench

LLM ShieldBench is a Vedansh Labs project for practical, transparent AI assistant safety evaluation. Contributions should keep the tool beginner-readable, research-friendly, and careful with safety-sensitive behavior.

## Project Philosophy

Good contributions should:

- Make evaluations easier to understand.
- Preserve transparent rule-based scoring unless a scoring change is explicitly reviewed.
- Improve safety, reliability, documentation, or release quality.
- Avoid feature creep in locked milestones.
- Keep Manual Paste as the default benchmark workflow.

## Local Setup

```bash
cd /Users/vedanshtembhre/llm-shieldbench
source .venv/bin/activate
python -m streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

## Test Commands

Run the smoke tests and compile check before proposing changes:

```bash
python3 scripts/v09_api_benchmark_smoke_test.py
python3 scripts/v08_adapter_smoke_test.py
python3 scripts/v07_adapter_smoke_test.py
python3 -m py_compile app.py src/benchmark.py src/model_adapters.py src/scoring.py src/report_generator.py
```

Automated tests must stay mock-only. They should not require real API keys, real provider accounts, or live network calls.

## Contribution Rules

- Do not change scoring thresholds casually.
- Do not change benchmark logic without a clear reason and focused tests.
- Keep Manual Paste as the default benchmark workflow.
- Keep API behavior behind explicit user action and confirmation where benchmark prompts may be sent externally.
- Do not commit secrets, `.env`, Streamlit secrets, outputs, exports, caches, `.venv`, or `.openclaw`.
- Do not add provider SDKs or new dependencies without explicit discussion.
- Do not hardcode API keys or include real keys in docs, tests, screenshots, or sample files.
- Keep documentation professional and aligned with Vedansh Labs: building human-centered AI from research to reality.

## Pull Request Guidance

For each pull request, include:

- What changed
- Why it changed
- Commands run
- Any safety or API-key handling considerations
- Screenshots only if they do not reveal secrets or private endpoints
