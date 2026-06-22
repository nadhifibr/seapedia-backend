import uuid
from django.db import models

class Discount(models.Model):
    TYPE_CHOICES = [
        ('VOUCHER', 'Voucher'),
        ('PROMO', 'Promo'),
    ]
    VALUE_TYPE_CHOICES = [
        ('PERCENT', 'Percent'),
        ('FIXED', 'Fixed'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    code = models.CharField(max_length=50, unique=True)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    value_type = models.CharField(max_length=20, choices=VALUE_TYPE_CHOICES)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

class Voucher(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    discount = models.OneToOneField(Discount, on_delete=models.CASCADE, related_name='voucher')
    max_usage = models.IntegerField()
    used_count = models.IntegerField(default=0)

class Promo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    discount = models.OneToOneField(Discount, on_delete=models.CASCADE, related_name='promo')
    description = models.TextField(blank=True)
