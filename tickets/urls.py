from django.urls import path
from .views import TicketListCreateView, TicketDetailView


urlpatterns = [
    # Define API routes relative to the project's /api/ prefix.
    path("tickets/", TicketListCreateView.as_view(), name="ticket-list-create"),
    path("tickets/<int:pk>/", TicketDetailView.as_view(), name="ticket-detail"),
]
