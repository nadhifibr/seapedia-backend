import uuid
from django.db import models
from apps.users.models import SellerProfile

class Store(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.OneToOneField(SellerProfile, on_delete=models.CASCADE, related_name='store')
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
