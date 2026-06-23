from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.db import transaction
from .models import DeliveryAddress
from .serializers import DeliveryAddressSerializer
from apps.users.models import BuyerProfile

class BuyerPermissionMixin:
    permission_classes = [IsAuthenticated]
    
    def get_buyer_profile(self, user):
        if not user.roles or 'BUYER' not in user.roles:
            raise PermissionDenied("Only buyers can manage addresses.")
        try:
            return user.buyer_profile
        except BuyerProfile.DoesNotExist:
            raise PermissionDenied("Buyer profile not found.")

class DeliveryAddressListCreateView(BuyerPermissionMixin, generics.ListCreateAPIView):
    serializer_class = DeliveryAddressSerializer

    def get_queryset(self):
        buyer = self.get_buyer_profile(self.request.user)
        return DeliveryAddress.objects.filter(buyer=buyer).order_by('-is_default', 'id')

    def perform_create(self, serializer):
        buyer = self.get_buyer_profile(self.request.user)
        is_default = serializer.validated_data.get('is_default', False)
        
        with transaction.atomic():
            if is_default:
                DeliveryAddress.objects.filter(buyer=buyer, is_default=True).update(is_default=False)
            elif not DeliveryAddress.objects.filter(buyer=buyer).exists():
                # First address is always default
                is_default = True
                
            serializer.save(buyer=buyer, is_default=is_default)

class DeliveryAddressDetailView(BuyerPermissionMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DeliveryAddressSerializer
    lookup_field = 'id'

    def get_queryset(self):
        buyer = self.get_buyer_profile(self.request.user)
        return DeliveryAddress.objects.filter(buyer=buyer)

    def perform_update(self, serializer):
        buyer = self.get_buyer_profile(self.request.user)
        is_default = serializer.validated_data.get('is_default')
        
        with transaction.atomic():
            if is_default:
                DeliveryAddress.objects.filter(buyer=buyer, is_default=True).exclude(id=self.get_object().id).update(is_default=False)
            serializer.save()
