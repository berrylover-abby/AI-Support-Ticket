from rest_framework import serializers
from .models import Ticket

# To validate inputs.
# indicate data types for POST and GET.
class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id","title","description","created_at"]
        read_only_fields = ["id","created_at"]