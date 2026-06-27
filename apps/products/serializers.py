from rest_framework import serializers
from apps.stores.serializers import StoreSerializer, SimpleStoreSerializer
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'store', 'name', 'category', 'description', 'price', 'stock', 'image_url', 'is_active', 'created_at']
        read_only_fields = ['id', 'store', 'created_at']

    def validate_stock(self, value):
        if self.instance is None and value < 1:
            raise serializers.ValidationError("Stock minimal harus 1 saat membuat produk baru.")
        if value < 0:
            raise serializers.ValidationError("Stock tidak boleh kurang dari 0.")
        return value

class PublicProductSerializer(serializers.ModelSerializer):
    store = SimpleStoreSerializer(read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'store', 'name', 'category', 'description', 'price', 'stock', 'image_url', 'sold_count', 'average_rating', 'is_active', 'created_at']
