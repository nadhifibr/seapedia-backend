from rest_framework import serializers
from .models import Store

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        from apps.products.models import Product
        model = Product
        fields = ['id', 'name', 'price', 'image_url']

class StoreSerializer(serializers.ModelSerializer):
    recent_products = serializers.SerializerMethodField()
    total_sold = serializers.IntegerField(read_only=True, default=0)
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=1, read_only=True, default=0.0)

    class Meta:
        model = Store
        fields = ['id', 'name', 'slug', 'description', 'image_url', 'location', 'created_at', 'recent_products', 'total_sold', 'average_rating']
        read_only_fields = ['id', 'slug', 'created_at']

    def get_recent_products(self, obj):
        from apps.products.models import Product
        products = Product.objects.filter(store=obj, is_active=True).order_by('-created_at')[:3]
        return SimpleProductSerializer(products, many=True).data
