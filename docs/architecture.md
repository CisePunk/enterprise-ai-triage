# Architecture Notes

## Runtime View

```text
React UI
  -> FastAPI API
    -> Triage service provider interface
      -> Mock provider today
      -> OpenAI / Anthropic / Mistral adapters later
    -> SQLite ticket repository
```

## Key Design Choices

- The frontend stays operational: intake form, KPI cards, distributions, and ticket register.
- The backend owns classification, risk scoring, escalation, and recommendation logic.
- The AI provider is abstracted behind `TriageProvider`, so the application does not depend on one LLM vendor.
- SQLite is used for local persistence and GitHub demo simplicity.
- The mock provider is deterministic so tests, demos, and screenshots remain stable.

## Production Hardening Path

- Replace SQLite with PostgreSQL.
- Add authentication, RBAC, and organization-level tenancy.
- Add LLM gateway with policy checks, prompt templates, response validation, and audit logging.
- Add ITSM integrations such as ServiceNow, Jira Service Management, PagerDuty, or Opsgenie.
- Add async workers for long-running enrichment and remediation workflows.
