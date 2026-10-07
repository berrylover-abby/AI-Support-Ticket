from rest_framework import generics
from .models import Ticket
from .serializers import TicketSerializer

# Backend API logic goes here.

# how to create ticket.
class TicketListCreateView(generics.ListCreateAPIView):
    # set up a rule for fetching ticket order
    queryset = Ticket.objects.order_by("-created_at")
     # tell TicketSerializer to convert data type into JSON
    serializer_class = TicketSerializer

# GET: find required ticket, convert into JSON using serializer and return to the frontend.
class TicketDetailView(generics.RetrieveAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
