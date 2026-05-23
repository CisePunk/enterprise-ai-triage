import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.ai_providers import get_triage_provider
from app.models import DashboardKpis, HealthResponse, Ticket, TicketCreate, TriageResult
from app.repository import create_ticket, get_dashboard_kpis, init_db, list_tickets, seed_demo_data


APP_VERSION = "0.1.0"
AI_PROVIDER_NAME = os.getenv("AI_PROVIDER", "mock")
provider = get_triage_provider(AI_PROVIDER_NAME)

app = FastAPI(
    title="Enterprise AI Triage API",
    version=APP_VERSION,
    description="LLM-agnostic service management triage prototype for AI, IT operations, and governance workflows.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()
    seed_demo_data(provider.classify)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        provider=provider.name,
        database="sqlite",
        version=APP_VERSION,
    )


@app.post("/triage/preview", response_model=TriageResult)
def preview_triage(ticket: TicketCreate) -> TriageResult:
    return provider.classify(ticket)


@app.post("/tickets", response_model=Ticket)
def submit_ticket(ticket: TicketCreate) -> Ticket:
    result = provider.classify(ticket)
    return create_ticket(ticket, result)


@app.get("/tickets", response_model=list[Ticket])
def get_tickets() -> list[Ticket]:
    return list_tickets()


@app.get("/dashboard", response_model=DashboardKpis)
def dashboard() -> DashboardKpis:
    return get_dashboard_kpis()
