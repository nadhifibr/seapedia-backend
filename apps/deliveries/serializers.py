from rest_framework import serializers
from .models import DeliveryJob
from apps.orders.serializers import OrderItemSerializer

class DeliveryJobSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='order.store.name', read_only=True)
    buyer_name = serializers.CharField(source='order.buyer.user.username', read_only=True)
    buyer_address = serializers.CharField(source='order.address_snapshot', read_only=True)
    order_id = serializers.CharField(source='order.id', read_only=True)
    delivery_method = serializers.CharField(source='order.delivery_method', read_only=True)
    items = OrderItemSerializer(source='order.items', many=True, read_only=True)
    
    class Meta:
        model = DeliveryJob
        fields = [
            'id', 'order_id', 'status', 'driver_earning', 
            'store_name', 'buyer_name', 'buyer_address', 
            'delivery_method', 'taken_at', 'completed_at',
            'items', 'driver_id'
        ]
