from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Priority(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"
    critical = "Critical"


class TicketCategory(str, Enum):
    incident = "Incident"
    service_request = "Service Request"
    security_risk = "Security Risk"
    ai_use_case = "AI Use Case"
    governance_issue = "Governance Issue"


class EscalationTeam(str, Enum):
    support = "Support"
    devops = "DevOps"
    security = "Security"
    business_owner = "Business Owner"
    ai_governance = "AI Governance"


class TicketCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=160)
    description: str = Field(..., min_length=10, max_length=4000)
    priority: Priority
    business_impact: str = Field(..., min_length=3, max_length=500)
    technical_area: str = Field(..., min_length=2, max_length=120)


class TriageResult(BaseModel):
    category: TicketCategory
    risk_score: int = Field(..., ge=1, le=5)
    escalation: EscalationTeam
    recommendation: str
    provider: str
    rationale: str


class Ticket(TicketCreate):
    id: int
    category: TicketCategory
    risk_score: int
    escalation: EscalationTeam
    recommendation: str
    rationale: str
    provider: str
    created_at: str


class DashboardKpis(BaseModel):
    total_tickets: int
    average_risk_score: float
    priority_counts: dict[str, int]
    category_counts: dict[str, int]
    escalation_counts: dict[str, int]
    high_risk_tickets: int


class HealthResponse(BaseModel):
    status: str
    provider: str
    database: str
    version: str


class TicketUpdateQuantityPlaceholder(BaseModel):
    note: Optional[str] = None
