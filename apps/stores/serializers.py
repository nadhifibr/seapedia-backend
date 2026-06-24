from rest_framework import serializers
from .models import Store

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'slug', 'description', 'image_url', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']
