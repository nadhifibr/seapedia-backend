from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import DeliveryJob
from .serializers import DeliveryJobSerializer

class DeliveryJobViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = DeliveryJobSerializer

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'driver_profile'):
            return DeliveryJob.objects.none()
            
        # Only show jobs that are available
        return DeliveryJob.objects.filter(status='AVAILABLE').order_by('-order__created_at')
