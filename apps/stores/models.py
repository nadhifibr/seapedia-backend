import uuid
from django.db import models
from django.utils.text import slugify
from apps.users.models import SellerProfile

class LocationChoices(models.TextChoices):
    JAKARTA = 'JAKARTA', 'Jakarta'
    TANGERANG = 'TANGERANG', 'Tangerang'
    ANYER = 'ANYER', 'Anyer'
    BALI = 'BALI', 'Bali'
    LOMBOK = 'LOMBOK', 'Lombok'
    BATAM = 'BATAM', 'Batam'
    MANADO = 'MANADO', 'Manado'
    MAKASSAR = 'MAKASSAR', 'Makassar'
    SURABAYA = 'SURABAYA', 'Surabaya'
    RAJA_AMPAT = 'RAJA_AMPAT', 'Raja Ampat'

class Store(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.OneToOneField(SellerProfile, on_delete=models.CASCADE, related_name='store')
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=50, choices=LocationChoices.choices, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
