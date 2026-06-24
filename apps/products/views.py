from django.db.models import Q
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
        queryset = Product.objects.filter(is_active=True)
        
        # 1. Store Slug Filter (from previous task)
        store_slug = self.request.query_params.get('store_slug')
        if store_slug:
            queryset = queryset.filter(store__slug=store_slug)
            
        # 2. Search
        q = self.request.query_params.get('q')
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | 
                Q(description__icontains=q) | 
                Q(store__name__icontains=q)
            )
            
        # 3. Category Filter
        category = self.request.query_params.get('category')
        if category and category != 'ALL':
            queryset = queryset.filter(category=category)
            
        # 4. Sorting
        sort = self.request.query_params.get('sort', 'newest')
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        else:
            queryset = queryset.order_by('-created_at') # default 'newest'
            
        return queryset

class PublicProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = PublicProductSerializer
    permission_classes = [AllowAny]
