import os
import django
import random
from decimal import Decimal
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
from apps.users.models import User, UserRole, BuyerProfile, SellerProfile, DriverProfile
from apps.stores.models import Store
from apps.products.models import Product
from apps.orders.models import Order, OrderItem, OrderStatusHistory
from apps.reviews.models import ProductReview, AppReview
from apps.addresses.models import DeliveryAddress
from apps.cart.models import Cart, CartItem
from apps.wallet.models import WalletTransaction
from apps.discounts.models import Discount, Voucher, Promo
from apps.deliveries.models import DeliveryJob, SellerTransaction

PRODUCT_NAMES = ["Joran Pancing Pro", "Set Alat Selam", "Kacamata Renang", "Oksigen Portabel", "Fin Scuba", "Snorkel Gear", "Perahu Karet Inflatable", "Cooler Box 50L", "Pelampung Dewasa", "Tali Pancing Kuat", "Jaring Ikan Besar", "Baju Renang Anti UV", "Senter Bawah Air", "Pisau Selam Survival", "Pelampung Anak"]
CATEGORIES = [
    ("FISHING_GEAR", "/categories/fishing_gear.png"),
    ("DIVING_GEAR", "/categories/diving_gear.png"),
    ("MARINE_EQUIPMENT", "/categories/marine_equipment.png"),
    ("OCEAN_APPAREL", "/categories/ocean_apparel.png"),
    ("OCEAN_ACCESSORIES", "/categories/ocean_accessories.png"),
    ("OTHER", "/categories/other_marine.png")
]
REVIEWS = ["Barangnya bagus banget", "Sesuai deskripsi, mantap!", "Pengiriman agak lama tapi barang oke", "Kualitas terjamin", "Biasa aja sih", "Luar biasa, recommended seller!", "Suka banget, pas dipakai", "Agak lecet dikit tapi gapapa", "Bakal order lagi di sini"]
APP_REVIEWS = ["Aplikasi gampang banget dipakai!", "UI nya cakep parah", "Banyak promo dan voucher", "Driver cepat sampai", "Bisa jualan dengan mudah", "Sangat membantu nelayan lokal"]

def get_password(name):
    return name if len(name) >= 8 else name * 2

def run_seed():
    print("Starting unified seed process...")

    # 1. SPECIAL CHIIKAWA CHARACTERS
    print("Seeding special characters...")
    characters = [
        {"name": "hachiware", "roles": ["BUYER", "SELLER"]},
        {"name": "momonga", "roles": ["BUYER"]},
        {"name": "kurimanju", "roles": ["SELLER"]},
        {"name": "shisa", "roles": ["DRIVER", "BUYER"]},
        {"name": "rakko", "roles": ["ADMIN"]},
        {"name": "chiikawa", "roles": ["BUYER"]},
        {"name": "usagi", "roles": ["BUYER"]},
    ]

    for char in characters:
        name = char["name"]
        email = f"{name}@gmail.com"
        password = get_password(name)
        
        user, created = User.objects.get_or_create(username=name, defaults={'email': email})
        if created:
            user.set_password(password)
            user.save()
            
        for role in char["roles"]:
            UserRole.objects.get_or_create(user=user, role=role)
            
            if role == "BUYER":
                buyer, _ = BuyerProfile.objects.get_or_create(user=user, defaults={'wallet_balance': 1000000})
                DeliveryAddress.objects.get_or_create(
                    buyer=buyer, 
                    label="Rumah", 
                    defaults={"full_address": f"Jalan {name.capitalize()} No 1", "is_default": True, "phone_number": "08123456789", "location": "JAKARTA"}
                )
                Cart.objects.get_or_create(buyer=buyer)
                WalletTransaction.objects.get_or_create(
                    buyer=buyer, type="TOPUP", amount=1000000, defaults={"description": "Initial Topup"}
                )
            elif role == "SELLER":
                seller, _ = SellerProfile.objects.get_or_create(user=user)
                store, _ = Store.objects.get_or_create(
                    seller=seller, 
                    defaults={
                        "name": f"Toko {name.capitalize()}", 
                        "description": f"Toko serba ada milik {name.capitalize()}",
                        "location": "JAKARTA"
                    }
                )
            elif role == "DRIVER":
                DriverProfile.objects.get_or_create(user=user)

    # 2. MASSIVE GENERIC USERS
    print("Seeding massive generic users...")
    sellers = []
    for i in range(1, 11):
        username = f"seller_pro_{i}"
        user, created = User.objects.get_or_create(username=username, defaults={'email': f"{username}@example.com"})
        if created:
            user.set_password('password123')
            user.save()
            UserRole.objects.get_or_create(user=user, role='SELLER')
            profile, _ = SellerProfile.objects.get_or_create(user=user)
            store, _ = Store.objects.get_or_create(
                seller=profile,
                defaults={
                    'name': f"Toko Bahari {i}",
                    'slug': f"toko-bahari-{i}",
                    'description': f"Toko alat laut terbaik nomor {i}",
                    'location': "JAKARTA" if i % 2 == 0 else "SURABAYA"
                }
            )
            sellers.append(store)
        else:
            if hasattr(user, 'seller_profile') and hasattr(user.seller_profile, 'store'):
                sellers.append(user.seller_profile.store)

    buyers = []
    for i in range(1, 51):
        username = f"buyer_man_{i}"
        user, created = User.objects.get_or_create(username=username, defaults={'email': f"{username}@example.com"})
        if created:
            user.set_password('password123')
            user.save()
            UserRole.objects.get_or_create(user=user, role='BUYER')
            profile, _ = BuyerProfile.objects.get_or_create(user=user, defaults={'wallet_balance': 5000000})
            DeliveryAddress.objects.get_or_create(
                buyer=profile, label="Rumah", defaults={"full_address": f"Jl. Samudera No {i}", "is_default": True, "location": "SURABAYA"}
            )
            Cart.objects.get_or_create(buyer=profile)
            WalletTransaction.objects.get_or_create(
                buyer=profile, type="TOPUP", amount=5000000, defaults={"description": "Massive Topup"}
            )
            buyers.append(profile)
        else:
            if hasattr(user, 'buyer_profile'):
                buyers.append(user.buyer_profile)

    drivers = []
    for i in range(1, 6):
        username = f"driver_pro_{i}"
        user, created = User.objects.get_or_create(username=username, defaults={'email': f"{username}@example.com"})
        if created:
            user.set_password('password123')
            user.save()
            UserRole.objects.get_or_create(user=user, role='DRIVER')
            profile, _ = DriverProfile.objects.get_or_create(user=user)
            drivers.append(profile)
        else:
            if hasattr(user, 'driver_profile'):
                drivers.append(user.driver_profile)
                
    # Add chiikawa drivers to list
    for char in characters:
        if "DRIVER" in char["roles"]:
            try:
                user = User.objects.get(username=char["name"])
                if hasattr(user, 'driver_profile'):
                    drivers.append(user.driver_profile)
            except: pass
            
    # Add chiikawa sellers to list
    for char in characters:
        if "SELLER" in char["roles"]:
            try:
                user = User.objects.get(username=char["name"])
                if hasattr(user, 'seller_profile') and hasattr(user.seller_profile, 'store'):
                    sellers.append(user.seller_profile.store)
            except: pass

    # 3. DISCOUNTS / PROMOS
    print("Seeding discounts and vouchers...")
    if not Discount.objects.filter(code='VOUCHER50').exists():
        d1 = Discount.objects.create(type='VOUCHER', code='VOUCHER50', value=Decimal('50000.00'), value_type='FIXED', expires_at=timezone.now() + timedelta(days=30), is_active=True)
        Voucher.objects.create(discount=d1, max_usage=50, used_count=0)

    if not Discount.objects.filter(code='PROMO10').exists():
        d2 = Discount.objects.create(type='PROMO', code='PROMO10', value=Decimal('10.00'), value_type='PERCENT', expires_at=timezone.now() + timedelta(days=30), is_active=True)
        Promo.objects.create(discount=d2, description='Special 10% discount for all items!')

    # 4. PRODUCTS
    print("Seeding products...")
    all_products = []
    for store in sellers:
        num_products = random.randint(5, 15)
        for _ in range(num_products):
            cat, img = random.choice(CATEGORIES)
            name = f"{random.choice(PRODUCT_NAMES)} - V{random.randint(1, 999)}"
            price = Decimal(random.randint(5, 500) * 1000)
            product, _ = Product.objects.get_or_create(
                store=store, name=name,
                defaults={'description': f"Deskripsi keren untuk {name}", 'price': price, 'stock': random.randint(5, 100), 'category': cat, 'image_url': img}
            )
            all_products.append(product)

    # 5. CHIikawa CART POPULATION
    print("Seeding carts...")
    if all_products:
        product_to_add = all_products[0]
        for buyer in BuyerProfile.objects.all():
            if hasattr(buyer.user, 'seller_profile') and hasattr(buyer.user.seller_profile, 'store') and buyer.user.seller_profile.store == product_to_add.store:
                continue
            cart = getattr(buyer, 'cart', None)
            if not cart:
                cart = Cart.objects.create(buyer=buyer)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product_to_add, defaults={"quantity": 1})
            if created:
                cart.store = product_to_add.store
                cart.save()

    # 6. APP REVIEWS
    print("Seeding app reviews...")
    for i in range(10):
        name = random.choice([b.user.username for b in buyers])
        if not AppReview.objects.filter(reviewer_name=name).exists():
            AppReview.objects.create(
                reviewer_name=name, rating=random.choice([4, 5]), comment=random.choice(APP_REVIEWS)
            )

    # 7. ORDERS, DELIVERIES & REVIEWS
    print("Seeding orders, deliveries, and product reviews...")
    for buyer in buyers:
        num_orders = random.randint(1, 3)
        for _ in range(num_orders):
            product = random.choice(all_products)
            qty = random.randint(1, 3)
            price = product.price
            subtotal = price * qty
            
            order = Order.objects.create(
                buyer=buyer, store=product.store, delivery_method="REGULAR", address_snapshot="Jl. Fiktif No. 123",
                subtotal=subtotal, delivery_fee=Decimal('15000.00'), tax_amount=subtotal * Decimal('0.11'),
                total=subtotal + Decimal('15000.00') + (subtotal * Decimal('0.11')), status="PESANAN_SELESAI"
            )
            
            OrderItem.objects.create(order=order, product=product, product_name=product.name, price_snapshot=price, quantity=qty)
            
            OrderStatusHistory.objects.create(order=order, status="PESANAN_SELESAI", note="Pesanan telah diterima oleh pembeli.")
            
            # Create a SellerTransaction
            SellerTransaction.objects.get_or_create(
                seller=product.store.seller, order=order, type="INCOME", defaults={"amount": subtotal}
            )
            
            # Create a DeliveryJob
            if drivers:
                driver = random.choice(drivers)
                DeliveryJob.objects.create(
                    order=order, driver=driver, status="DONE", driver_earning=Decimal('15000.00'),
                    taken_at=timezone.now() - timedelta(days=1), completed_at=timezone.now()
                )

            # Product Review
            if random.random() < 0.7:
                if not ProductReview.objects.filter(product=product, buyer=buyer).exists():
                    rating = random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.05, 0.1, 0.4, 0.4])[0]
                    ProductReview.objects.create(product=product, buyer=buyer, rating=rating, comment=random.choice(REVIEWS))

    print("=========================================")
    print("Seed process completed successfully!")
    print("=========================================")

if __name__ == "__main__":
    run_seed()
