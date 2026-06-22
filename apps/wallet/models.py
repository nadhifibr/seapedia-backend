import uuid
from django.db import models
from apps.users.models import BuyerProfile

class WalletTransaction(models.Model):
    TYPE_CHOICES = [
        ('TOPUP', 'Topup'),
        ('PAYMENT', 'Payment'),
        ('REFUND', 'Refund'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer = models.ForeignKey(BuyerProfile, on_delete=models.CASCADE, related_name='wallet_transactions')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
