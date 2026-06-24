from rest_framework import serializers
from .models import DeliveryAddress

class DeliveryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAddress
        fields = ['id', 'label', 'full_address', 'phone_number', 'location', 'is_default']
        read_only_fields = ['id']
