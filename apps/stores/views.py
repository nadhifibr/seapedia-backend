from django.db.models import Q
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.users.permissions import IsActiveSeller
from .models import Store
from .serializers import StoreSerializer

class MyStoreView(APIView):
    permission_classes = [IsAuthenticated, IsActiveSeller]

    def get(self, request):
        if not hasattr(request.user, 'seller_profile'):
            return Response({"detail": "User is not a seller."}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            store = request.user.seller_profile.store
            serializer = StoreSerializer(store)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Store.DoesNotExist:
            return Response({"detail": "Store not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        if not hasattr(request.user, 'seller_profile'):
            return Response({"detail": "User is not a seller."}, status=status.HTTP_403_FORBIDDEN)
            
        if hasattr(request.user.seller_profile, 'store'):
            return Response({"detail": "Store already exists. Use PUT/PATCH to update."}, status=status.HTTP_400_BAD_REQUEST)
            
        serializer = StoreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(seller=request.user.seller_profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def patch(self, request):
        if not hasattr(request.user, 'seller_profile'):
            return Response({"detail": "User is not a seller."}, status=status.HTTP_403_FORBIDDEN)
            
        try:
            store = request.user.seller_profile.store
        except Store.DoesNotExist:
            return Response({"detail": "Store not found."}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = StoreSerializer(store, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        return self.patch(request)

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from core.pagination import StandardResultsSetPagination

@method_decorator(cache_page(60 * 15), name='dispatch') # Cache for 15 minutes
class PublicStoreListView(generics.ListAPIView):
    serializer_class = StoreSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        from django.db.models import Prefetch
        from apps.products.models import Product
        
        products_prefetch = Prefetch(
            'products', 
            queryset=Product.objects.filter(is_active=True).order_by('-created_at'), 
            to_attr='cached_recent_products'
        )
        queryset = Store.objects.prefetch_related(products_prefetch).order_by('-created_at')
        q = self.request.query_params.get('q')
        location = self.request.query_params.get('location')
        
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) |
                Q(description__icontains=q)
            )
        if location and location != 'ALL':
            locations = location.split(',')
            queryset = queryset.filter(location__in=locations)
            
        return queryset

from django.db.models import Sum, Avg, DecimalField, Q
from django.db.models.functions import Coalesce

class PublicStoreDetailView(generics.RetrieveAPIView):
    serializer_class = StoreSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return Store.objects.all().annotate(
            total_sold=Coalesce(Sum('products__sold_count'), 0),
            average_rating=Coalesce(
                Avg('products__average_rating', filter=Q(products__average_rating__gt=0)), 
                0.0, 
                output_field=DecimalField(max_digits=3, decimal_places=1)
            )
        )
