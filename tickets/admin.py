
from django.contrib import admin, messages
from .models import Ticket

# register model and settings, connect model with admin
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "created_at")
    list_filter = ("status",)
    readonly_fields = ("ai_result", "status", "created_at")
    actions = ["confirm_review"]


    @admin.action(description="Confirm selected tickets")
    def confirm_review(self, request, queryset):
        for ticket in queryset:
            # collect reviews..
            review_fields = [
                ticket.reviewed_category,
                ticket.reviewed_priority,
                ticket.reviewed_summary,
                ticket.reviewed_reply,
            ]
            # only collect pending reviews...
            if ticket.status != Ticket.Status.PENDING_REVIEW:
                self.message_user(
                    request,
                    f"Ticket {ticket.id} is not pending review.",
                    level=messages.WARNING,
                )
                continue
            # make sure all fields are filled before confirming
            if not all(value.strip() for value in review_fields):
                self.message_user(
                    request,
                    f"Complete all review fields for ticket {ticket.id}.",
                    level=messages.WARNING,
                )
                continue
            
            # update status and show results.
            ticket.status = Ticket.Status.CONFIRMED
            ticket.save(update_fields=["status"])
            self.message_user(request, f"Ticket {ticket.id} confirmed.")