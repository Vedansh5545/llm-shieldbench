# Changelog

All notable milestone changes for LLM ShieldBench are summarized here.

## v1.0 Public Release Candidate

- Added public release documentation foundation.
- Added MIT license.
- Added security policy and responsible disclosure guidance.
- Added contributor setup, testing, and safety rules.
- Documented release-candidate positioning without adding new benchmark behavior.

## v0.9 API Benchmark Execution

- Added optional selected-case API benchmark execution.
- Required explicit confirmation before sending benchmark prompts to a configured API provider.
- Added runtime-enabled OpenAI-compatible adapter path.
- Reused existing benchmark scoring, report, download, and history flow.
- Added mock-only v0.9 API benchmark smoke test.

## v0.8 API-Based Model Testing

- Added optional one-prompt OpenAI-compatible API connection test.
- Added safe OpenAI-compatible adapter configuration.
- Added standard-library HTTP helper.
- Kept automated tests mock-only.
- Kept Manual Paste as the default benchmark workflow.

## v0.7 Model Adapter Foundation

- Added provider-neutral model adapter interface.
- Added Manual Paste, Disabled, and Mock adapters.
- Added helper for generating responses from adapter-backed cases.
- Added benchmark helper that reuses existing manual-response scoring.

## v0.6 Benchmark Analytics

- Added risk and severity analytics.
- Added category summary cards.
- Added weakest-category explanations.
- Improved benchmark result visualization.

## v0.5 Evaluation History

- Added session evaluation history.
- Added history exports to CSV, JSON, and Markdown.
- Added clear-history workflow.

## v0.4 Custom Benchmark Upload

- Added custom benchmark JSON upload.
- Added schema validation for custom benchmark cases.
- Added custom benchmark execution and exports.

## v0.3 Expanded Evaluation Logic

- Expanded failure taxonomy.
- Added severity labels.
- Improved instruction-following checks.
- Adjusted weak-refusal and scoring calibration behavior.

## v0.2 Benchmark Preview

- Added Benchmark Mode.
- Added built-in benchmark cases.
- Added category-wise scoring and weakest-category detection.
- Added benchmark Markdown and CSV exports.

## v0.1 Research Preview

- Added single-response evaluation.
- Added transparent rule-based scoring.
- Added Markdown report export.
- Added initial premium Streamlit UI foundation.
