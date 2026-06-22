import uuid
from django.db import models
from apps.users.models import BuyerProfile
from apps.stores.models import Store
from apps.products.models import Product
from apps.discounts.models import Discount

class Order(models.Model):
    DELIVERY_METHOD_CHOICES = [
        ('INSTANT', 'Instant'),
        ('NEXT_DAY', 'Next Day'),
        ('REGULAR', 'Regular'),
    ]
    STATUS_CHOICES = [
        ('SEDANG_DIKEMAS', 'Sedang Dikemas'),
        ('MENUNGGU_PENGIRIM', 'Menunggu Pengirim'),
        ('SEDANG_DIKIRIM', 'Sedang Dikirim'),
        ('PESANAN_SELESAI', 'Pesanan Selesai'),
        ('DIKEMBALIKAN', 'Dikembalikan'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer = models.ForeignKey(BuyerProfile, on_delete=models.CASCADE, related_name='orders')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='orders')
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHOD_CHOICES)
    address_snapshot = models.TextField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    is_refunded = models.BooleanField(default=False)
    overdue_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')
    product_name = models.CharField(max_length=255)
    price_snapshot = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.IntegerField()

class OrderStatusHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=50)
    note = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
