from django.urls import path
from .views import TicketListCreateView, TicketDetailView

# to deal with api/....
urlpatterns = [
    path("tickets/", TicketListCreateView.as_view(), name="ticket-list-create"),
    # tickets/1,2,3,4,5 to find the required ticket.
    path("tickets/<int:pk>/", TicketDetailView.as_view(), name="ticket-detail"),
]