# AI Governance Approach

This prototype treats AI triage as part of a governed help desk workflow.

## Controls

- A human-readable classification reason is stored with each ticket.
- Escalation remains explicit and reviewable.
- Risk score is bounded from 1 to 5.
- Provider output is mapped into controlled application values.
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
- classification reason

This keeps the operational workflow independent from the model vendor.

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
