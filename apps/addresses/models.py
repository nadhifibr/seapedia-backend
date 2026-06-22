import uuid
from django.db import models
from apps.users.models import BuyerProfile

class DeliveryAddress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer = models.ForeignKey(BuyerProfile, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=100)
    full_address = models.TextField()
    is_default = models.BooleanField(default=False)
