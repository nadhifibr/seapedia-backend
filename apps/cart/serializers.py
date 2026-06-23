from rest_framework import serializers
from .models import Cart, CartItem
from apps.products.serializers import PublicProductSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product_detail = PublicProductSerializer(source='product', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_detail', 'quantity', 'subtotal']
        read_only_fields = ['id']

    def get_subtotal(self, obj):
        return obj.quantity * obj.product.price

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    store_name = serializers.CharField(source='store.name', read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'store', 'store_name', 'items', 'total']

    def get_total(self, obj):
        return sum(item.quantity * item.product.price for item in obj.items.all())
