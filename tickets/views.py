import logging
import os
from django.shortcuts import render
from rest_framework import generics
from rest_framework.exceptions import ValidationError

from .llm import LLMError
from .models import Ticket
from .serializers import TicketSerializer
from .services import analyze_and_save_ticket


logger = logging.getLogger(__name__)


class TicketListCreateView(generics.ListCreateAPIView):
    queryset = Ticket.objects.order_by("-created_at")
    serializer_class = TicketSerializer

    def perform_create(self, serializer):
        # Persist the ticket before calling the model.
        ticket = serializer.save()

        try:
            # Analyze, validate, and save using the shared service.
            analyze_and_save_ticket(ticket)

        except (LLMError, ValidationError) as error:
            # Preserve the ticket and allow a manual retry in Admin.
            ticket.status = Ticket.Status.ANALYSIS_FAILED
            ticket.save(update_fields=["status"])
            logger.warning(
                "Ticket analysis failed: ticket_id=%s reason=%s",
                ticket.id,
                error,
            )

        else:
            logger.info(
                "Ticket analysis succeeded: ticket_id=%s",
                ticket.id,
            )


class TicketDetailView(generics.RetrieveAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer


def ticket_demo(request):
    # Disclose the server's analysis mode on the submission page.
    mode = os.environ.get("TICKET_AI_MODE", "mock")
    return render(request, "tickets/demo.html", {"analysis_mode": mode})
