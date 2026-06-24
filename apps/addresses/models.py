import uuid
from django.db import models
from apps.users.models import BuyerProfile
from django.core.validators import RegexValidator
from apps.stores.models import LocationChoices

class DeliveryAddress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer = models.ForeignKey(BuyerProfile, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=100)
    full_address = models.TextField()
    phone_number = models.CharField(
        max_length=15, 
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")],
        default=''
    )
    location = models.CharField(max_length=50, choices=LocationChoices.choices, null=True, blank=True)
    is_default = models.BooleanField(default=False)
