# LLM Cost and Token Control

The current prototype uses the mock provider:

```text
mock-enterprise-rules-v1
```

That means:

- no external LLM API calls
- no vendor token consumption
- no ticket content leaves the local application
- demo behavior is deterministic

## When Real LLM Providers Are Added

OpenAI, Anthropic, Mistral, or any other model provider should be connected through the provider adapter layer only.

Required controls:

- log provider, model, prompt version, input tokens, output tokens, and estimated cost
- set per-user, per-team, and per-environment token budgets
- add rate limits and request timeouts
- redact secrets, credentials, and unnecessary personal data before model calls
- store only the minimum prompt/response data needed for audit
- separate production, staging, and demo provider credentials
- fail closed when token budget or policy checks are exceeded

## Suggested Metadata Per Classification

```text
provider
model
prompt_version
input_tokens
output_tokens
estimated_cost
latency_ms
policy_status
data_sensitivity
```

This keeps AI usage measurable, governable, and defensible for enterprise operations.
