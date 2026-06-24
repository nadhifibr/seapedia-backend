from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from apps.users.models import User, UserRole, BuyerProfile, SellerProfile, DriverProfile
from apps.stores.models import Store
from apps.products.models import Product
from apps.discounts.models import Discount, Voucher, Promo
from apps.addresses.models import DeliveryAddress
import uuid

class Command(BaseCommand):
    help = 'Seeds the database with demo accounts, store, products, and discounts.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')
        password = 'Seapedia123!'

        # 1. ADMIN
        admin_user, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@seapedia.com'})
        if created:
            admin_user.set_password(password)
            admin_user.save()
            UserRole.objects.get_or_create(user=admin_user, role='ADMIN')
            self.stdout.write(self.style.SUCCESS('Created Admin: admin@seapedia.com'))

        # 2. SELLER
        seller_user, created = User.objects.get_or_create(username='seller', defaults={'email': 'seller@seapedia.com'})
        if created:
            seller_user.set_password(password)
            seller_user.save()
            UserRole.objects.get_or_create(user=seller_user, role='SELLER')
            seller_profile, _ = SellerProfile.objects.get_or_create(user=seller_user)
            
            store, store_created = Store.objects.get_or_create(
                seller=seller_profile, 
                defaults={'name': 'Toko Samudra Jaya', 'description': 'Toko peralatan laut terlengkap.'}
            )
            
            if store_created:
                Product.objects.create(
                    store=store, name='Pancingan Shimano', description='Alat pancing kuat.',
                    price=Decimal('150000.00'), stock=100, category='FISHING_GEAR'
                )
                Product.objects.create(
                    store=store, name='Baju Selam', description='Baju selam anti dingin.',
                    price=Decimal('500000.00'), stock=50, category='DIVING_GEAR'
                )
                Product.objects.create(
                    store=store, name='Pelampung', description='Pelampung standar.',
                    price=Decimal('75000.00'), stock=200, category='MARINE_EQUIPMENT'
                )
            self.stdout.write(self.style.SUCCESS('Created Seller: seller@seapedia.com with Store and Products'))

        # 3. BUYER
        buyer_user, created = User.objects.get_or_create(username='buyer', defaults={'email': 'buyer@seapedia.com'})
        if created:
            buyer_user.set_password(password)
            buyer_user.save()
            UserRole.objects.get_or_create(user=buyer_user, role='BUYER')
            buyer_profile, _ = BuyerProfile.objects.get_or_create(
                user=buyer_user, 
                defaults={'wallet_balance': Decimal('1000000.00')}
            )
            
            DeliveryAddress.objects.get_or_create(
                buyer=buyer_profile,
                defaults={'label': 'Rumah', 'full_address': 'Jl. Lautan Ilmu No. 1, Jakarta', 'phone_number': '+6281234567890', 'is_default': True}
            )
            self.stdout.write(self.style.SUCCESS('Created Buyer: buyer@seapedia.com with Wallet and Address'))

        # 4. DRIVER
        driver_user, created = User.objects.get_or_create(username='driver', defaults={'email': 'driver@seapedia.com'})
        if created:
            driver_user.set_password(password)
            driver_user.save()
            UserRole.objects.get_or_create(user=driver_user, role='DRIVER')
            DriverProfile.objects.get_or_create(user=driver_user)
            self.stdout.write(self.style.SUCCESS('Created Driver: driver@seapedia.com'))

        # 5. DISCOUNTS
        # Promo 10%
        if not Discount.objects.filter(code='PROMO10').exists():
            d1 = Discount.objects.create(
                type='PROMO', code='PROMO10', value=Decimal('10.00'), value_type='PERCENT',
                expires_at=timezone.now() + timezone.timedelta(days=365)
            )
            Promo.objects.create(discount=d1, description='Promo diskon 10% untuk semua pelanggan.')
            self.stdout.write(self.style.SUCCESS('Created Promo: PROMO10'))

        # Voucher 50k
        if not Discount.objects.filter(code='VOUCHER50K').exists():
            d2 = Discount.objects.create(
                type='VOUCHER', code='VOUCHER50K', value=Decimal('50000.00'), value_type='FIXED',
                expires_at=timezone.now() + timezone.timedelta(days=365)
            )
            Voucher.objects.create(discount=d2, max_usage=100)
            self.stdout.write(self.style.SUCCESS('Created Voucher: VOUCHER50K'))

        self.stdout.write(self.style.SUCCESS('Data seeding completed!'))
