# LLM ShieldBench v1.0 Release Checklist

Use this checklist before tagging a public v1.0 release candidate.

## Pre-release Git Checks

- Confirm the current branch is `main`.
- Confirm expected release-candidate commits are present.
- Confirm there are no accidental generated outputs, exports, caches, virtual environments, secrets, or private config files staged.
- Review the final diff before tagging.

```bash
git status
git log --oneline --decorate -10
git diff --stat
git diff
```

## Test Commands

Run from the repository root:

```bash
python3 scripts/v09_api_benchmark_smoke_test.py
python3 scripts/v08_adapter_smoke_test.py
python3 scripts/v07_adapter_smoke_test.py
python3 -m py_compile app.py src/benchmark.py src/model_adapters.py src/scoring.py src/report_generator.py
```

## App Manual Test Checklist

Start the app:

```bash
cd /Users/vedanshtembhre/llm-shieldbench
source .venv/bin/activate
python -m streamlit run app.py
```

Manual checks:

- Single Evaluation runs and shows trust score, risk level, strengths, issues, recommendation, and Markdown download.
- Benchmark Mode runs with Manual Paste selected by default.
- Built-in benchmark cases can be selected and evaluated.
- Custom benchmark upload accepts valid JSON and shows clear validation feedback for invalid JSON.
- Evaluation History records current-session results and exports CSV, JSON, and Markdown.
- Optional API Connection Test requires explicit user action.
- Optional API Benchmark Execution is confirmation-gated and remains optional.
- Reports and downloads do not include API keys or secrets.

## API Safety Checklist

- Do not commit `.env`, `.venv`, `.openclaw`, outputs, exports, caches, or API keys.
- Do not hardcode real API keys or include example real API keys.
- Do not share screenshots with API keys, private endpoint URLs, credentials, customer data, or confidential prompts.
- Manual Paste remains default.
- API benchmark execution is optional and confirmation-gated.
- API-related tests should stay mock-only and avoid real network calls.

## Documentation Checklist

- README reflects the current v1.0 feature set.
- SECURITY.md explains private reporting and secret handling expectations.
- CONTRIBUTING.md is appropriate for public contributors.
- CHANGELOG.md includes the intended v1.0 release notes.
- Issue templates are present for bug reports and feature requests.
- Public docs do not include secrets, private endpoints, or real credentials.

## Repo Hygiene Checklist

- No generated outputs, exports, caches, virtual environments, or local OpenClaw files are staged.
- No accidental edits to app logic, adapter logic, benchmark logic, scoring, or API behavior.
- No dependency changes unless explicitly intended.
- No private configs, local paths beyond documented run commands, or credentials are committed.
- License, security policy, contribution guide, and changelog are present.

## Things Not Included in v1.0

- Multi-model comparison.
- New provider SDK integrations.
- Background or automatic API benchmark execution.
- Production-grade hosted service deployment.
- A guarantee of complete model safety.

## Final Tag/Release Commands

Use the final version/tag name selected for the release candidate.

```bash
git status
git diff --stat
git add .github/ISSUE_TEMPLATE/bug_report.md \
  .github/ISSUE_TEMPLATE/feature_request.md \
  .github/ISSUE_TEMPLATE/config.yml \
  RELEASE_CHECKLIST.md
git commit -m "Add v1.0 GitHub release hygiene files"
git tag -a v1.0.0-rc1 -m "LLM ShieldBench v1.0.0 RC1"
git push origin main
git push origin v1.0.0-rc1
```
