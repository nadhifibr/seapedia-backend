import os
import django
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.discounts.models import Discount, Voucher, Promo

def run_seed():
    print("Seeding Discounts...")

    # Clear old ones to avoid uniqueness errors
    Discount.objects.all().delete()

    # Create a Voucher: VOUCHER50 (Rp 50,000 off), max usage 5
    d1 = Discount.objects.create(
        type='VOUCHER',
        code='VOUCHER50',
        value=Decimal('50000.00'),
        value_type='FIXED',
        expires_at=timezone.now() + timedelta(days=30),
        is_active=True
    )
    Voucher.objects.create(
        discount=d1,
        max_usage=5,
        used_count=0
    )

    # Create a Promo: PROMO10 (10% off)
    d2 = Discount.objects.create(
        type='PROMO',
        code='PROMO10',
        value=Decimal('10.00'),
        value_type='PERCENT',
        expires_at=timezone.now() + timedelta(days=30),
        is_active=True
    )
    Promo.objects.create(
        discount=d2,
        description='Special 10% discount for all items!'
    )
    
    # Create an Expired Promo: EXPIRED20 (20% off)
    d3 = Discount.objects.create(
        type='PROMO',
        code='EXPIRED20',
        value=Decimal('20.00'),
        value_type='PERCENT',
        expires_at=timezone.now() - timedelta(days=1),
        is_active=True
    )
    Promo.objects.create(
        discount=d3,
        description='This promo is already expired.'
    )

    print("Successfully seeded!")
    print("- VOUCHER50 (Fixed Rp 50.000, max usage: 5)")
    print("- PROMO10 (Percent 10%)")
    print("- EXPIRED20 (Percent 20%, expired)")

if __name__ == '__main__':
    run_seed()
