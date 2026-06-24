from rest_framework import serializers
from .models import AppReview, ProductReview
import bleach

class AppReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppReview
        fields = ['id', 'reviewer_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_comment(self, value):
        # Sanitize comment to prevent XSS
        cleaned_value = bleach.clean(value, tags=[], attributes={}, strip=True)
        return cleaned_value

    def validate_reviewer_name(self, value):
        cleaned_value = bleach.clean(value, tags=[], attributes={}, strip=True)
        return cleaned_value

class ProductReviewSerializer(serializers.ModelSerializer):
    buyer_name = serializers.CharField(source='buyer.user.get_full_name', read_only=True)

    class Meta:
        model = ProductReview
        fields = ['id', 'product', 'buyer', 'buyer_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'product', 'buyer', 'buyer_name', 'created_at']

    def validate_comment(self, value):
        if value:
            if len(value) > 500:
                raise serializers.ValidationError("Comment cannot exceed 500 characters.")
            cleaned_value = bleach.clean(value, tags=[], attributes={}, strip=True)
            return cleaned_value
        return value
