from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.users.permissions import IsActiveSeller
from rest_framework.exceptions import PermissionDenied
from .models import Product
from .serializers import ProductSerializer, PublicProductSerializer

class SellerProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsActiveSeller]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'seller_profile') and hasattr(user.seller_profile, 'store'):
            return Product.objects.filter(store=user.seller_profile.store).order_by('-created_at')
        return Product.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, 'seller_profile'):
            raise PermissionDenied("Hanya seller yang dapat membuat produk.")
        if not hasattr(user.seller_profile, 'store'):
            raise PermissionDenied("Anda belum memiliki toko. Silakan buat toko terlebih dahulu.")
            
        serializer.save(store=user.seller_profile.store)

class SellerProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsActiveSeller]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'seller_profile') and hasattr(user.seller_profile, 'store'):
            return Product.objects.filter(store=user.seller_profile.store)
        return Product.objects.none()

class PublicProductListView(generics.ListAPIView):
    serializer_class = PublicProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).order_by('-created_at')
        store_slug = self.request.query_params.get('store_slug')
        if store_slug:
            queryset = queryset.filter(store__slug=store_slug)
        return queryset

class PublicProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = PublicProductSerializer
    permission_classes = [AllowAny]
