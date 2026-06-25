import uuid
from django.db import models
from apps.stores.models import Store
from django.core.validators import MinValueValidator
from decimal import Decimal

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField()
    CATEGORY_CHOICES = [
        ('FISHING_GEAR', 'Fishing Gear'),
        ('DIVING_GEAR', 'Diving Gear'),
        ('MARINE_EQUIPMENT', 'Marine Equipment'),
        ('OCEAN_APPAREL', 'Ocean Apparel'),
        ('OCEAN_ACCESSORIES', 'Ocean Accessories'),
        ('OTHER', 'Other'),
    ]
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('100.00'))])
    stock = models.IntegerField(default=0, validators=[MinValueValidator(1)])
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='OTHER')
    image_url = models.URLField(blank=True, null=True)
    sold_count = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    average_rating = models.DecimalField(max_digits=3, decimal_places=1, default=Decimal('0.0'))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
