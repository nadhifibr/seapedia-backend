import uuid
from django.db import models
from apps.orders.models import Order
from apps.users.models import DriverProfile, SellerProfile

class DeliveryJob(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('TAKEN', 'Taken'),
        ('DONE', 'Done'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery_job')
    driver = models.ForeignKey(DriverProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='delivery_jobs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    driver_earning = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    taken_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

class SellerTransaction(models.Model):
    TYPE_CHOICES = [
        ('INCOME', 'Income'),
        ('REVERSAL', 'Reversal'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name='transactions')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='seller_transactions')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
