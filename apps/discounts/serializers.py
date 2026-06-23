from rest_framework import serializers
from .models import Discount, Voucher, Promo

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ['id', 'type', 'code', 'value', 'value_type', 'expires_at', 'is_active']
        read_only_fields = ['type']

class VoucherSerializer(serializers.ModelSerializer):
    discount = DiscountSerializer()

    class Meta:
        model = Voucher
        fields = ['id', 'discount', 'max_usage', 'used_count']
        read_only_fields = ['used_count']

    def create(self, validated_data):
        discount_data = validated_data.pop('discount')
        discount_data['type'] = 'VOUCHER'
        discount = Discount.objects.create(**discount_data)
        voucher = Voucher.objects.create(discount=discount, **validated_data)
        return voucher

class PromoSerializer(serializers.ModelSerializer):
    discount = DiscountSerializer()

    class Meta:
        model = Promo
        fields = ['id', 'discount', 'description']

    def create(self, validated_data):
        discount_data = validated_data.pop('discount')
        discount_data['type'] = 'PROMO'
        discount = Discount.objects.create(**discount_data)
        promo = Promo.objects.create(discount=discount, **validated_data)
        return promo
