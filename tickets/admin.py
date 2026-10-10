
import logging

from django.contrib import admin, messages
from rest_framework.exceptions import ValidationError

from .models import Ticket
from .services import analyze_and_save_ticket


logger = logging.getLogger(__name__)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "created_at")
    list_filter = ("status",)
    readonly_fields = ("ai_result", "status", "created_at")
    actions = ["run_analysis", "confirm_review"]

    @admin.action(description="Analyze selected tickets (mock)")
    def run_analysis(self, request, queryset):
        for ticket in queryset:
            if ticket.status not in [
                Ticket.Status.PENDING_ANALYSIS,
                Ticket.Status.ANALYSIS_FAILED,
            ]:
                self.message_user(
                    request,
                    f"Ticket {ticket.id} cannot be analyzed in its current state.",
                    level=messages.WARNING,
                )
                continue

            try:
                analyze_and_save_ticket(ticket)
            except ValidationError:
                logger.warning(
                    "Ticket analysis failed: ticket_id=%s reason=invalid_output",
                    ticket.id,
                )
                ticket.status = Ticket.Status.ANALYSIS_FAILED
                ticket.save(update_fields=["status"])
                self.message_user(
                    request,
                    f"Analysis failed for ticket {ticket.id}: invalid output.",
                    level=messages.ERROR,
                )
            else:
                logger.info(
                    "Ticket analysis succeeded: ticket_id=%s",
                    ticket.id,
                )
                self.message_user(request, f"Ticket {ticket.id} analyzed.")

    @admin.action(description="Confirm selected tickets")
    def confirm_review(self, request, queryset):
        for ticket in queryset:
            if ticket.status != Ticket.Status.PENDING_REVIEW:
                self.message_user(
                    request,
                    f"Ticket {ticket.id} is not pending review.",
                    level=messages.WARNING,
                )
                continue

            review_fields = [
                ticket.reviewed_category,
                ticket.reviewed_priority,
                ticket.reviewed_summary,
                ticket.reviewed_reply,
            ]
            if not all(value.strip() for value in review_fields):
                self.message_user(
                    request,
                    f"Complete all review fields for ticket {ticket.id}.",
                    level=messages.WARNING,
                )
                continue

            ticket.status = Ticket.Status.CONFIRMED
            ticket.save(update_fields=["status"])
            self.message_user(request, f"Ticket {ticket.id} confirmed.")