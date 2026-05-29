# Security Policy

LLM ShieldBench is a rule-based benchmark and evaluation tool for AI assistant safety research. It can help surface safety, privacy, hallucination, and instruction-following issues, but it is not a guarantee of complete model safety.

## Reporting Security Issues

If you find a security issue, please report it privately to the project maintainer instead of opening a public issue with sensitive details.

When reporting, include:

- A concise description of the issue
- Steps to reproduce, using fake data only
- The affected file, feature, or workflow
- Any suggested mitigation, if known

Do not include real API keys, secrets, credentials, private endpoint URLs, customer data, or confidential prompts in the report.

## Secret Handling

Never post API keys or secrets in public issues, discussions, pull requests, screenshots, benchmark cases, sample files, reports, or exported results.

For local testing:

- Use placeholder values in docs and tests.
- Keep `.env`, Streamlit secrets, credentials, and private configs out of git.
- Do not paste real API keys into source files.
- Do not share screenshots that reveal API keys or private endpoint credentials.

## API Safety Expectations

Manual Paste remains the default and safest benchmark workflow. Optional API execution is user-triggered and confirmation-gated.

API keys must not be stored in reports, downloads, history, generated outputs, exported files, or logs. If you add or review API-related changes, keep automated tests mock-only and avoid real network calls.

## Responsible Disclosure

Please give the maintainer reasonable time to review and address security reports before public disclosure. The goal is to keep the project useful, safe, and trustworthy for students, engineers, researchers, and builders.
