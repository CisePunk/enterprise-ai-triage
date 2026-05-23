# Enterprise AI Triage - Full Walkthrough

This document explains the technical and operational reasoning behind Enterprise AI Triage.

The project is intentionally small. It is designed to show how AI-related intake can be handled with enterprise controls: classification, risk scoring, escalation, audit context, provider abstraction, and cost awareness.

The important part is not a sophisticated model. The important part is the workflow around the model boundary.

## Problem Context

Enterprise teams receive mixed requests through many channels:

- production incidents
- service requests
- access and onboarding tasks
- security risks
- AI automation ideas
- governance and compliance questions

Without a common intake layer, teams spend time deciding what the request is, who owns it, how risky it is, and whether governance review is required.

AI adoption makes this harder. A request may look like a business automation idea but also involve customer data, compliance exposure, or operational impact. The triage layer needs to notice those signals early.

This prototype addresses that at a manageable scale: each ticket is validated, classified, scored, routed, explained, and persisted.

## Design Principles

The design follows a few practical rules:

- AI supports a decision; it does not silently make the final operational decision.
- Output is constrained to known categories and escalation teams.
- Risk scoring is bounded and easy to inspect.
- The rationale is stored with the ticket.
- Provider identity is stored so decisions can be traced back to the source.
- The provider is replaceable without changing the UI or database contract.
- Cost and token usage are treated as future operational metrics, not as an afterthought.
- Security and governance signals are prioritized over generic automation signals.

## Runtime Architecture

```text
React frontend
    |
    v
FastAPI backend
    |
    v
Triage provider interface
    |
    v
Mock enterprise rules provider
    |
    v
SQLite persistence
```

### Frontend

The React frontend is an operational dashboard. It contains:

- ticket intake form
- KPI cards
- priority, category, and escalation summaries
- ticket register

The frontend does not own classification or routing rules. It submits structured input and displays the backend result.

### Backend

FastAPI owns the application workflow:

- validates the ticket payload
- calls the triage provider
- persists the original ticket and classification result
- returns dashboard aggregates

Pydantic models provide a typed boundary for request and response data.

### Provider Layer

The provider interface is intentionally narrow:

```python
class TriageProvider:
    def classify(self, ticket: TicketCreate) -> TriageResult:
        ...
```

That keeps the rest of the system independent from a specific model vendor.

The current implementation uses:

```text
mock-enterprise-rules-v1
```

Adapter placeholders exist for OpenAI, Anthropic, and Mistral. They are not wired into the prototype because the first version is meant to be deterministic, local, and free of external data transfer.

### Persistence

SQLite is used for local persistence. It is enough for the prototype because it stores real ticket history without requiring external infrastructure.

A production path would replace SQLite with PostgreSQL or another managed relational database, add migrations, and introduce tenant boundaries where needed.

## Data Model

The ticket intake requires:

- title
- description
- priority
- business impact
- technical area

The triage result contains:

- category
- risk score
- escalation team
- recommendation
- provider
- rationale

The constrained categories are:

- `Incident`
- `Service Request`
- `Security Risk`
- `AI Use Case`
- `Governance Issue`

The constrained escalation teams are:

- `Support`
- `DevOps`
- `Security`
- `Business Owner`
- `AI Governance`

These enums matter. They prevent free-form model output from directly shaping operational routing.

## End-To-End Flow

1. A user submits a ticket through the frontend.
2. FastAPI validates the payload with Pydantic.
3. The backend calls `provider.classify(ticket)`.
4. The provider returns a constrained `TriageResult`.
5. The repository stores both the original ticket fields and the classification result.
6. The dashboard reads aggregate KPIs and the ticket register.

The flow is simple, but it preserves the operational evidence needed for later review.

## Classification Logic

The mock provider combines:

- title
- description
- business impact
- technical area

into one lowercase text field. It then applies keyword groups in a deliberate order.

### Category Order

Security is checked first:

```text
security, vulnerability, breach, phishing, cve, iam, zero trust
```

Governance is checked next:

```text
policy, compliance, gdpr, risk committee, audit, governance, approval
```

AI use cases are checked after security and governance:

```text
ai, llm, model, prompt, rag, copilot, automation use case
```

Incident and service request signals are checked after that:

```text
down, outage, broken, incident, failed, latency, degraded
request, access, provision, new user, onboarding, change
```

The fallback category is:

```text
Service Request
```

The order is not accidental. A phrase like "AI assistant exposes customer data vulnerability" should be handled as a security risk first. That is a safer enterprise default than routing it as a normal AI use case.

## Risk Scoring

Risk starts at `1`.

Priority contributes:

```text
Low      +0
Medium   +1
High     +2
Critical +3
```

Business or production impact adds `+1` when the combined text contains:

```text
revenue, customer, production, sla, regulatory, blocked
```

Security and governance categories add another `+1`.

The score is capped at `5`.

This is intentionally bounded. The goal is not precision. The goal is a clear and reviewable severity signal that can support routing and dashboard reporting.

## Escalation Logic

Escalation is selected after category and risk signals:

```text
Security Risk      -> Security
Governance Issue   -> AI Governance
AI Use Case        -> Business Owner or AI Governance
High/Critical Incident -> DevOps
Default            -> Support
```

For AI use cases, the provider looks for business-oriented terms such as:

```text
roi, business, process
```

If those appear, the request is routed to `Business Owner`; otherwise it goes to `AI Governance`.

This is a practical split. Some AI ideas need business ownership first. Others need governance review before design work starts.

## Recommendation Logic

Recommendations use service-management language rather than generic AI language.

Examples:

- Incidents: open an incident bridge, confirm blast radius, assign owner, and communicate against SLA.
- Service requests: validate scope, confirm approval path, and use standard fulfillment.
- Security risks: trigger security triage, preserve evidence, assess exposure, and define containment.
- AI use cases: capture business outcome, data sensitivity, feasibility, and success metrics before solution design.
- Governance/high-risk cases: document decision criteria and record risk acceptance or mitigation.

This keeps the system focused on the next operational action.

## API Summary

The backend exposes:

- `GET /health`
- `POST /tickets`
- `POST /triage/preview`
- `GET /tickets`
- `GET /dashboard`

`POST /triage/preview` runs classification without persistence. `POST /tickets` classifies and stores the ticket.

The dashboard endpoint returns:

- total tickets
- average risk score
- high-risk ticket count
- counts by priority
- counts by category
- counts by escalation

## LLM-Agnostic Design

The provider contract is the main boundary:

```text
TicketCreate -> TriageResult
```

A future LLM provider should not leak model-specific behavior into the UI, repository, or dashboard code. It should return the same schema as the mock provider.

When real providers are added, each classification should capture:

- provider
- model
- prompt version
- input tokens
- output tokens
- estimated cost
- latency
- policy result
- data sensitivity level

That metadata turns model usage into something measurable and governable.

## Enterprise Constraints Considered

The prototype reflects constraints that matter in enterprise environments:

- operational ownership must be explicit
- security review should not depend on someone noticing risk late
- AI use cases need business value and data sensitivity checks
- audit context should be stored with the decision
- automated output should be bounded by schema
- model providers should be replaceable
- external data transfer should be avoided during early evaluation
- token usage and cost should be visible when real providers are introduced
- dependency vulnerabilities should be reviewed and remediated

## Security And CVE Review

Security review covered the frontend npm dependencies and the backend Python environment.

Current reviewed status:

```text
Frontend npm audit: 0 known vulnerabilities
Backend pip-audit after remediation: 0 known vulnerabilities
```

One local backend tooling issue was found:

```text
pip 26.0.1
```

Reported CVEs:

- `CVE-2026-3219`
- `CVE-2026-6357`

The local backend virtual environment was remediated by upgrading `pip` to `26.1.1`, followed by a clean `pip-audit` result.

This matters even though `pip` is not application logic. Build tools and developer environments are still part of the delivery surface.

## Production Hardening Path

Before production use, the system would need:

- authentication and RBAC
- tenant isolation
- HTTPS and secure secrets management
- PostgreSQL or equivalent production storage
- database migrations
- immutable audit logs
- backup and retention policy
- PII and secret detection
- LLM gateway with redaction, policy checks, and response validation
- CI dependency scanning and SBOM generation
- integration with ITSM tools such as ServiceNow or Jira Service Management
- escalation hooks for tools such as PagerDuty or Opsgenie

## How To Run Locally

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Default URLs:

- Backend: `http://127.0.0.1:8000`
- API docs: `http://127.0.0.1:8000/docs`
- Frontend: `http://127.0.0.1:5173`

## Positioning

The project is useful because it shows disciplined AI adoption work in a small codebase.

It connects AI automation, IT operations, security review, governance, service delivery, and business impact. The classifier is deliberately simple; the architecture around it is the point.
