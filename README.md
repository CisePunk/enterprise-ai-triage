# Enterprise AI Triage

Italian version: [README-it.md](README-it.md)

Enterprise AI Triage is a small web application designed to speed up work inside a structured help desk. The operator enters the initial ticket information; the system then applies triage rules automatically to classify the request, estimate risk, and route it to the right team.

The project uses a clear, scalable architecture that can be adapted to different organizational needs. The workflow is designed with compliance, security, cost control, and operational ownership in mind from the start.

The goal is to place automation inside a traceable operational process: the ticket is still written by a person, while category, risk score, escalation, recommendation, and rationale are produced by the backend in a consistent and reviewable way.

## What It Does

The application accepts the starting information for a ticket: title, description, priority, business impact, and technical area.

From that input, the backend automatically returns:

- category
- risk score from 1 to 5
- escalation team
- operational recommendation
- rationale
- provider name

Supported categories:

- `Incident`
- `Service Request`
- `Security Risk`
- `AI Use Case`
- `Governance Issue`

Supported escalation teams:

- `Support`
- `DevOps`
- `Security`
- `Business Owner`
- `AI Governance`

The dashboard provides a compact operational view: total tickets, average risk, high-risk count, priority distribution, category distribution, escalation distribution, and the ticket register.

## What It Is For

Each request is classified, scored, routed to the right team, and stored with a readable rationale. This helps the help desk reduce time spent on first-level sorting while keeping a record of the decisions made.

## Design Principles

- Use AI to support correct case routing and trigger the right operational path: change management, technical intervention, security review, or governance.
- Keep routing and risk scoring based on criteria that can be reviewed.
- Store the classification reason with each ticket.
- Limit automated output to controlled values, avoiding free-form or ambiguous categories.
- Keep the AI provider separate from the rest of the application, so the LLM engine can change without rewriting the operational workflow.
- Treat AI cost and token usage as operational data.
- Prefer deterministic behavior for early evaluation and demos.
- Design the workflow around ownership, escalation, and governance.

## Architecture

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

The current provider is deterministic and local:

```text
mock-enterprise-rules-v1
```

OpenAI, Anthropic, and Mistral provider classes are present as adapter placeholders. The UI and persistence model do not depend on a specific LLM vendor.

## Governance Model

The application treats classification as a governed workflow:

- provider output is limited to known categories
- risk score is bounded from 1 to 5
- classification reason is stored with every ticket
- escalation is explicit and reviewable
- provider name is persisted
- the mock provider sends no data externally
- future model providers must return the same response format

Requests with security signals take priority over AI use cases. For example, if a ticket mentions an AI assistant exposing customer data, the system routes it toward security review before treating it as an automation proposal.

## Enterprise Constraints Considered

This prototype explicitly accounts for constraints that appear in real enterprise adoption work:

- unclear ownership across IT, business, security, and governance teams
- sensitive data exposure in AI workflows
- auditability of automated recommendations
- bounded and reviewable risk scoring
- provider lock-in avoidance
- token and cost governance for future LLM providers
- dependency and CVE review as part of the delivery surface
- a path from local SQLite persistence to production-grade storage

## Technology Choices

- **React** for the operational intake and dashboard UI.
- **FastAPI** for typed API boundaries and readable service logic.
- **SQLite** for local persistence without external infrastructure.
- **Provider abstraction** to keep model-specific behavior outside the core workflow.
- **Mock provider** to keep early evaluation deterministic, cost-free, and safe for local use.

## API Surface

The backend exposes a small API:

- `GET /health`
- `POST /tickets`
- `POST /triage/preview`
- `GET /tickets`
- `GET /dashboard`

Detailed endpoint behavior and classification logic are documented in:

- [docs/full-walkthrough-en.md](docs/full-walkthrough-en.md)
- [docs/full-walkthrough-it.md](docs/full-walkthrough-it.md)

## Local Setup

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
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

## Security And Cost Notes

The current implementation does not call external LLM APIs.

```text
External LLM token usage: 0
External LLM cost: 0
External ticket data shared with model vendors: 0
```

Dependency review was performed on the frontend and backend environment. A vulnerable local `pip` version was identified and remediated by upgrading from `26.0.1` to `26.1.1`; the follow-up `pip-audit` result reported no known vulnerabilities.

More detail:

- [docs/llm-cost-control.md](docs/llm-cost-control.md)
- [docs/security-cve-review.md](docs/security-cve-review.md)

## Current Scope

This is a prototype, not a production system.

It deliberately keeps authentication, RBAC, tenant isolation, production storage, immutable audit logs, and ITSM integrations out of the first version. Those are the correct next steps if the system is moved beyond local evaluation.

## Positioning

This project demonstrates enterprise-oriented AI adoption thinking:

- operational triage before automation
- governance before scale
- explainability before autonomous action
- cost visibility before provider rollout
- architecture boundaries before vendor integration

The main point is not that the classifier is complex. The point is that the workflow is shaped like something an enterprise team could extend, review, and govern.
