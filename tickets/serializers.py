from rest_framework import serializers
from .models import Ticket

# To validate inputs.
# indicate data types for POST and GET.
class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id","title","description","created_at"]
        read_only_fields = ["id","created_at"]

class TicketAnalysisSerializer(serializers.Serializer):
    category = serializers.ChoiceField(
        choices=["account", "billing", "technical", "other"]
    )
    priority = serializers.ChoiceField(
        choices=["low", "medium", "high"]
    )
    summary = serializers.CharField()
    suggested_reply = serializers.CharField()