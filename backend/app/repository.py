import sqlite3
from pathlib import Path
from typing import Any

from app.models import DashboardKpis, Ticket, TicketCreate, TriageResult


DB_PATH = Path(__file__).resolve().parent.parent / "triage.db"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                priority TEXT NOT NULL,
                business_impact TEXT NOT NULL,
                technical_area TEXT NOT NULL,
                category TEXT NOT NULL,
                risk_score INTEGER NOT NULL,
                escalation TEXT NOT NULL,
                recommendation TEXT NOT NULL,
                rationale TEXT NOT NULL,
                provider TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def create_ticket(ticket: TicketCreate, result: TriageResult) -> Ticket:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO tickets (
                title,
                description,
                priority,
                business_impact,
                technical_area,
                category,
                risk_score,
                escalation,
                recommendation,
                rationale,
                provider
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticket.title,
                ticket.description,
                ticket.priority.value,
                ticket.business_impact,
                ticket.technical_area,
                result.category.value,
                result.risk_score,
                result.escalation.value,
                result.recommendation,
                result.rationale,
                result.provider,
            ),
        )

        row = connection.execute(
            "SELECT * FROM tickets WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()

    return _row_to_ticket(row)


def list_tickets() -> list[Ticket]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM tickets ORDER BY created_at DESC, id DESC"
        ).fetchall()

    return [_row_to_ticket(row) for row in rows]


def get_dashboard_kpis() -> DashboardKpis:
    tickets = list_tickets()
    total = len(tickets)

    priority_counts = _count_by(tickets, "priority")
    category_counts = _count_by(tickets, "category")
    escalation_counts = _count_by(tickets, "escalation")
    average_risk = sum(ticket.risk_score for ticket in tickets) / total if total else 0
    high_risk = len([ticket for ticket in tickets if ticket.risk_score >= 4])

    return DashboardKpis(
        total_tickets=total,
        average_risk_score=round(average_risk, 2),
        priority_counts=priority_counts,
        category_counts=category_counts,
        escalation_counts=escalation_counts,
        high_risk_tickets=high_risk,
    )


def seed_demo_data(provider_result_factory) -> None:
    with get_connection() as connection:
        existing = connection.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]

    if existing:
        return

    samples = [
        TicketCreate(
            title="Production API latency affecting enterprise customers",
            description="Checkout orchestration API is degraded and customer-facing SLA is at risk.",
            priority="Critical",
            business_impact="Revenue impact and customer trust risk for a production workload.",
            technical_area="Platform Operations",
        ),
        TicketCreate(
            title="Evaluate RAG assistant for service desk knowledge articles",
            description="Business team wants an AI use case to reduce support handling time with a governed RAG assistant.",
            priority="Medium",
            business_impact="Potential productivity improvement and measurable ticket deflection.",
            technical_area="AI Automation",
        ),
        TicketCreate(
            title="Possible IAM vulnerability in contractor access process",
            description="Security review found stale access and potential compliance exposure.",
            priority="High",
            business_impact="Regulatory and audit exposure if not remediated.",
            technical_area="Identity and Access Management",
        ),
    ]

    for sample in samples:
        create_ticket(sample, provider_result_factory(sample))


def _row_to_ticket(row: sqlite3.Row) -> Ticket:
    return Ticket(**dict(row))


def _count_by(tickets: list[Ticket], attribute: str) -> dict[str, int]:
    counts: dict[str, int] = {}

    for ticket in tickets:
        value = getattr(ticket, attribute)
        key = value.value if hasattr(value, "value") else str(value)
        counts[key] = counts.get(key, 0) + 1

    return counts
