from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from .models import ProductReview

@receiver(post_save, sender=ProductReview)
@receiver(post_delete, sender=ProductReview)
def update_product_average_rating(sender, instance, **kwargs):
    product = instance.product
    avg_rating = ProductReview.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
    if avg_rating is not None:
        product.average_rating = round(avg_rating, 1)
    else:
        product.average_rating = 0.0
    product.save(update_fields=['average_rating'])
