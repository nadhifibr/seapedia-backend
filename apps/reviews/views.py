from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import AppReview
from .serializers import AppReviewSerializer

class AppReviewViewSet(viewsets.ModelViewSet):
    queryset = AppReview.objects.all().order_by('-created_at')
    serializer_class = AppReviewSerializer
    permission_classes = [AllowAny]
