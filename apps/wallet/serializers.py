from rest_framework import serializers
from .models import WalletTransaction
from apps.users.models import BuyerProfile

class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = ['id', 'type', 'amount', 'description', 'created_at']
        read_only_fields = ['id', 'type', 'created_at']

class TopupSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
