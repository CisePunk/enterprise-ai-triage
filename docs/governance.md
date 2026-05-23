# AI Governance Approach

This prototype treats AI triage as a governed decision-support workflow, not as an autonomous final decision maker.

## Controls

- Human-readable rationale is stored with each classification.
- Escalation remains explicit and reviewable.
- Risk score is bounded from 1 to 5.
- Provider output is mapped into strict application enums.
- Mock provider avoids sending sensitive data to third-party systems during early evaluation.
- Real LLM providers should log token usage, estimated cost, model, prompt version, and policy status.
- Token budgets and rate limits should be enforced before production use.

## LLM-Agnostic Pattern

The provider contract is:

```text
TicketCreate -> TriageResult
```

Any future LLM adapter must return the same schema:

- category
- risk score
- escalation
- recommendation
- provider
- rationale

This keeps business workflow logic independent from the model vendor.

## Cost Governance

The prototype currently uses a mock provider, so external API token usage is zero.

When adding real LLM providers, each classification should capture:

- input tokens
- output tokens
- estimated cost
- provider and model
- prompt version
- latency
- policy result

This makes AI cost visible as an operational KPI rather than an invisible platform expense.
