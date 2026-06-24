from rest_framework import serializers
from apps.users.models import User
from apps.stores.models import Store
from apps.products.models import Product
from apps.orders.models import Order
from apps.discounts.models import Discount
from apps.deliveries.models import DeliveryJob

class AdminUserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    wallet_balance = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'roles', 'wallet_balance', 'created_at']

    def get_roles(self, obj):
        return [role.role for role in obj.roles.all()]

    def get_wallet_balance(self, obj):
        if hasattr(obj, 'buyer_profile'):
            return str(obj.buyer_profile.wallet_balance)
        return "0.00"

class AdminStoreSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='seller.user.username', read_only=True)

    class Meta:
        model = Store
        fields = ['id', 'name', 'owner', 'created_at']

class AdminProductSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'store_name', 'price', 'stock', 'category', 'is_active']

class AdminOrderSerializer(serializers.ModelSerializer):
    buyer_username = serializers.CharField(source='buyer.user.username', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'buyer_username', 'store_name', 'status', 'total', 'delivery_method', 'created_at', 'overdue_at']

class AdminDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ['id', 'code', 'type', 'value', 'value_type', 'is_active', 'expires_at']

class AdminDeliveryJobSerializer(serializers.ModelSerializer):
    driver_username = serializers.SerializerMethodField()
    order_id = serializers.CharField(source='order.id', read_only=True)

    class Meta:
        model = DeliveryJob
        fields = ['id', 'order_id', 'driver_username', 'status', 'taken_at', 'completed_at']

    def get_driver_username(self, obj):
        if obj.driver and hasattr(obj.driver, 'user'):
            return obj.driver.user.username
        return None
