import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.users.models import User, UserRole, BuyerProfile, SellerProfile, DriverProfile
from apps.stores.models import Store
from apps.products.models import Product
from apps.addresses.models import DeliveryAddress
from apps.cart.models import Cart, CartItem
from apps.wallet.models import WalletTransaction

def get_password(name):
    return name if len(name) >= 8 else name * 2

def seed_data():
    characters = [
        {"name": "hachiware", "roles": ["BUYER", "SELLER"]},
        {"name": "momonga", "roles": ["BUYER"]},
        {"name": "kurimanju", "roles": ["SELLER"]},
        {"name": "shisa", "roles": ["DRIVER", "BUYER"]},
        {"name": "rakko", "roles": ["ADMIN", "BUYER"]},
    ]

    print("Starting seed process...")

    for char in characters:
        name = char["name"]
        email = f"{name}@gmail.com"
        password = get_password(name)
        
        # create or get user
        user, created = User.objects.get_or_create(username=name, defaults={'email': email})
        if created:
            user.set_password(password)
            user.save()
            print(f"Created user: {name}")
        else:
            print(f"User {name} already exists.")
            
        for role in char["roles"]:
            UserRole.objects.get_or_create(user=user, role=role)
            
            if role == "BUYER":
                buyer, b_created = BuyerProfile.objects.get_or_create(user=user, defaults={'wallet_balance': 1000000})
                
                # Address
                DeliveryAddress.objects.get_or_create(
                    buyer=buyer, 
                    label="Rumah", 
                    defaults={
                        "full_address": f"Jalan {name.capitalize()} No 1", 
                        "is_default": True
                    }
                )
                
                # Cart
                Cart.objects.get_or_create(buyer=buyer)
                
                # Wallet Transaction
                WalletTransaction.objects.get_or_create(
                    buyer=buyer, 
                    type="TOPUP", 
                    amount=1000000, 
                    description="Initial Topup"
                )
                
            elif role == "SELLER":
                seller, _ = SellerProfile.objects.get_or_create(user=user)
                store, _ = Store.objects.get_or_create(
                    seller=seller, 
                    defaults={
                        "name": f"Toko {name.capitalize()}", 
                        "description": f"Toko serba ada milik {name.capitalize()}"
                    }
                )
                
                # Products
                Product.objects.get_or_create(
                    store=store, 
                    name=f"Alat Pancing {name.capitalize()}", 
                    defaults={
                        "description": f"Alat pancing terbaik dari {name.capitalize()}", 
                        "price": 150000, 
                        "stock": 10, 
                        "category": "FISHING_GEAR"
                    }
                )
                Product.objects.get_or_create(
                    store=store, 
                    name=f"Baju Selam {name.capitalize()}", 
                    defaults={
                        "description": f"Baju selam nyaman dari {name.capitalize()}", 
                        "price": 250000, 
                        "stock": 5, 
                        "category": "OCEAN_APPAREL"
                    }
                )
                
            elif role == "DRIVER":
                DriverProfile.objects.get_or_create(user=user)

    print("Adding items to carts...")
    # Add some items to carts to demonstrate cart functionality
    products = Product.objects.all()
    if products.exists():
        product_to_add = products.first()
        buyers = BuyerProfile.objects.all()
        for buyer in buyers:
            try:
                cart = buyer.cart
            except Exception:
                cart = Cart.objects.create(buyer=buyer)
                
            # Don't add if the buyer is also the seller of the product
            try:
                seller_profile = buyer.user.seller_profile
                if seller_profile.store == product_to_add.store:
                    continue
            except Exception:
                pass

            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, 
                product=product_to_add, 
                defaults={"quantity": 1}
            )
            if created:
                cart.store = product_to_add.store
                cart.save()

    # Make sure chiikawa and usagi also have basic profiles if they don't have them
    for existing_name in ["chiikawa", "usagi"]:
        try:
            existing_user = User.objects.get(username=existing_name)
            UserRole.objects.get_or_create(user=existing_user, role="BUYER")
            buyer, _ = BuyerProfile.objects.get_or_create(user=existing_user, defaults={'wallet_balance': 500000})
            DeliveryAddress.objects.get_or_create(
                buyer=buyer, 
                label="Rumah", 
                defaults={"full_address": f"Jalan {existing_name.capitalize()} No 1", "is_default": True}
            )
            Cart.objects.get_or_create(buyer=buyer)
        except User.DoesNotExist:
            print(f"User {existing_name} not found, skipping...")

    print("Seed process completed successfully!")

if __name__ == "__main__":
    seed_data()
