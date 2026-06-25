from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import F
from .models import OrderStatusHistory

@receiver(post_save, sender=OrderStatusHistory)
def increment_sold_count(sender, instance, created, **kwargs):
    if created and instance.status == 'PESANAN_SELESAI':
        order = instance.order
        for item in order.items.all():
            if item.product:
                product = item.product
                product.sold_count = F('sold_count') + item.quantity
                product.save(update_fields=['sold_count'])
