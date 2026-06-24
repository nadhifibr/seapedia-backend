from rest_framework import serializers
from .models import AppReview
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
