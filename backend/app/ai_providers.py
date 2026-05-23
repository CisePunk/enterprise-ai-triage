from abc import ABC, abstractmethod

from app.models import EscalationTeam, TicketCategory, TicketCreate, TriageResult


class TriageProvider(ABC):
    name: str

    @abstractmethod
    def classify(self, ticket: TicketCreate) -> TriageResult:
        raise NotImplementedError


class MockEnterpriseTriageProvider(TriageProvider):
    name = "mock-enterprise-rules-v1"

    def classify(self, ticket: TicketCreate) -> TriageResult:
        text = " ".join(
            [
                ticket.title,
                ticket.description,
                ticket.business_impact,
                ticket.technical_area,
            ]
        ).lower()

        category = self._category(text)
        risk_score = self._risk_score(ticket, text, category)
        escalation = self._escalation(category, text, ticket.priority.value)
        recommendation = self._recommendation(category, escalation, risk_score)
        rationale = self._rationale(category, risk_score, escalation)

        return TriageResult(
            category=category,
            risk_score=risk_score,
            escalation=escalation,
            recommendation=recommendation,
            provider=self.name,
            rationale=rationale,
        )

    def _category(self, text: str) -> TicketCategory:
        security_terms = ["security", "vulnerability", "breach", "phishing", "cve", "iam", "zero trust"]
        ai_terms = ["ai", "llm", "model", "prompt", "rag", "copilot", "automation use case"]
        governance_terms = ["policy", "compliance", "gdpr", "risk committee", "audit", "governance", "approval"]
        request_terms = ["request", "access", "provision", "new user", "onboarding", "change"]
        incident_terms = ["down", "outage", "broken", "incident", "failed", "latency", "degraded"]

        if any(term in text for term in security_terms):
            return TicketCategory.security_risk
        if any(term in text for term in governance_terms):
            return TicketCategory.governance_issue
        if any(term in text for term in ai_terms):
            return TicketCategory.ai_use_case
        if any(term in text for term in incident_terms):
            return TicketCategory.incident
        if any(term in text for term in request_terms):
            return TicketCategory.service_request

        return TicketCategory.service_request

    def _risk_score(self, ticket: TicketCreate, text: str, category: TicketCategory) -> int:
        score = 1

        priority_weight = {
            "Low": 0,
            "Medium": 1,
            "High": 2,
            "Critical": 3,
        }
        score += priority_weight[ticket.priority.value]

        if any(term in text for term in ["revenue", "customer", "production", "sla", "regulatory", "blocked"]):
            score += 1

        if category in [TicketCategory.security_risk, TicketCategory.governance_issue]:
            score += 1

        return min(score, 5)

    def _escalation(
        self,
        category: TicketCategory,
        text: str,
        priority: str,
    ) -> EscalationTeam:
        if category == TicketCategory.security_risk:
            return EscalationTeam.security
        if category == TicketCategory.governance_issue:
            return EscalationTeam.ai_governance
        if category == TicketCategory.ai_use_case:
            if "roi" in text or "business" in text or "process" in text:
                return EscalationTeam.business_owner
            return EscalationTeam.ai_governance
        if category == TicketCategory.incident and priority in ["High", "Critical"]:
            return EscalationTeam.devops
        return EscalationTeam.support

    def _recommendation(
        self,
        category: TicketCategory,
        escalation: EscalationTeam,
        risk_score: int,
    ) -> str:
        if category == TicketCategory.incident:
            return "Open an incident bridge, confirm blast radius, assign owner, and communicate status against SLA."
        if category == TicketCategory.service_request:
            return "Validate request scope, confirm approval path, and route through the standard fulfillment workflow."
        if category == TicketCategory.security_risk:
            return "Trigger security triage, preserve evidence, assess exposure, and define containment before remediation."
        if category == TicketCategory.ai_use_case:
            return "Capture business outcome, data sensitivity, feasibility, and success metrics before solution design."
        if risk_score >= 4 or escalation == EscalationTeam.ai_governance:
            return "Route to governance review, document decision criteria, and record risk acceptance or mitigation."
        return "Review ownership, classify impact, and define the next operational action."

    def _rationale(
        self,
        category: TicketCategory,
        risk_score: int,
        escalation: EscalationTeam,
    ) -> str:
        return (
            f"Classified as {category.value} with risk {risk_score}/5; "
            f"recommended escalation is {escalation.value} based on priority, impact, and keyword signals."
        )


class OpenAIProvider(TriageProvider):
    name = "openai-placeholder"

    def classify(self, ticket: TicketCreate) -> TriageResult:
        raise NotImplementedError("OpenAI provider adapter is intentionally not wired in this prototype.")


class AnthropicProvider(TriageProvider):
    name = "anthropic-placeholder"

    def classify(self, ticket: TicketCreate) -> TriageResult:
        raise NotImplementedError("Anthropic provider adapter is intentionally not wired in this prototype.")


class MistralProvider(TriageProvider):
    name = "mistral-placeholder"

    def classify(self, ticket: TicketCreate) -> TriageResult:
        raise NotImplementedError("Mistral provider adapter is intentionally not wired in this prototype.")


def get_triage_provider(provider_name: str | None = None) -> TriageProvider:
    providers = {
        "mock": MockEnterpriseTriageProvider,
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "mistral": MistralProvider,
    }

    provider_class = providers.get((provider_name or "mock").lower(), MockEnterpriseTriageProvider)
    return provider_class()
