import uuid
from django.db import models
from apps.users.models import BuyerProfile
from apps.stores.models import Store
from apps.products.models import Product

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer = models.OneToOneField(BuyerProfile, on_delete=models.CASCADE, related_name='cart')
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True, related_name='carts')

class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.IntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')
