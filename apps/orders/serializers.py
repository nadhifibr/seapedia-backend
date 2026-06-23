from rest_framework import serializers
from .models import Order, OrderItem, OrderStatusHistory

class OrderItemSerializer(serializers.ModelSerializer):
    product_image = serializers.URLField(source='product.image_url', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_image', 'price_snapshot', 'quantity']

class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = ['status', 'note', 'changed_at']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'buyer', 'store', 'store_name', 'delivery_method', 'address_snapshot', 
            'subtotal', 'discount_amount', 'delivery_fee', 'tax_amount', 'total', 
            'status', 'is_refunded', 'created_at', 'items', 'status_history'
        ]
        read_only_fields = ['buyer', 'store', 'address_snapshot', 'subtotal', 'discount_amount', 'delivery_fee', 'tax_amount', 'total', 'status']

class CheckoutSummarySerializer(serializers.Serializer):
    delivery_method = serializers.ChoiceField(choices=Order.DELIVERY_METHOD_CHOICES)
    address_id = serializers.UUIDField(required=False, allow_null=True)

class CheckoutSerializer(serializers.Serializer):
    delivery_method = serializers.ChoiceField(choices=Order.DELIVERY_METHOD_CHOICES)
    address_id = serializers.UUIDField()
