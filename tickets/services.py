
from .models import Ticket
from .serializers import TicketAnalysisSerializer
import os

from .llm import LLMError, analyze_with_llm


def mock_analyze_ticket(ticket):
    return {
        "category": "other",
        "priority": "medium",
        "summary": f"Support request: {ticket.title}",
        "suggested_reply": (
            "Thank you for contacting us. "
            "We will review your request and follow up shortly."
        ),
    }

def analyze_ticket(ticket):
    # Default to mock mode for local development.
    mode = os.environ.get("TICKET_AI_MODE", "mock")

    if mode == "mock":
        return mock_analyze_ticket(ticket)

    if mode == "openai":
        return analyze_with_llm(ticket)

    # Reject unsupported modes instead of silently choosing a provider.
    raise LLMError("Unsupported TICKET_AI_MODE. Use mock or openai.")


def analyze_and_save_ticket(ticket):
    allowed_statuses = [
        Ticket.Status.PENDING_ANALYSIS,
        Ticket.Status.ANALYSIS_FAILED,
    ]
    if ticket.status not in allowed_statuses:
        raise ValueError("Only pending or failed tickets can be analyzed.")

    raw_result = analyze_ticket(ticket)
    serializer = TicketAnalysisSerializer(data=raw_result)
    serializer.is_valid(raise_exception=True)
    result = serializer.validated_data

    ticket.ai_result = result
    ticket.reviewed_category = result["category"]
    ticket.reviewed_priority = result["priority"]
    ticket.reviewed_summary = result["summary"]
    ticket.reviewed_reply = result["suggested_reply"]
    ticket.status = Ticket.Status.PENDING_REVIEW

    ticket.save(update_fields=[
        "ai_result",
        "reviewed_category",
        "reviewed_priority",
        "reviewed_summary",
        "reviewed_reply",
        "status",
    ])