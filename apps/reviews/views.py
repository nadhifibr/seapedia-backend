from rest_framework import viewsets, generics, status
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.db.models import Avg, Count
from .models import AppReview, ProductReview
from .serializers import AppReviewSerializer, ProductReviewSerializer
from apps.products.models import Product
from apps.orders.models import Order

class AppReviewViewSet(viewsets.ModelViewSet):
    queryset = AppReview.objects.all().order_by('-created_at')
    serializer_class = AppReviewSerializer
    permission_classes = [AllowAny]

class ProductReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return ProductReview.objects.filter(product_id=product_id).order_by('-created_at')
        
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        product_id = self.kwargs['product_id']
        stats = ProductReview.objects.filter(product_id=product_id).aggregate(
            average_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        
        return Response({
            'stats': {
                'average_rating': round(stats['average_rating'], 1) if stats['average_rating'] else 0,
                'total_reviews': stats['total_reviews']
            },
            'reviews': serializer.data
        })

    def post(self, request, *args, **kwargs):
        product_id = self.kwargs['product_id']
        user = request.user
        
        if not hasattr(user, 'buyer_profile'):
            return Response({'detail': 'Only buyers can leave reviews.'}, status=status.HTTP_403_FORBIDDEN)
            
        buyer = user.buyer_profile
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
            
        # Check if buyer already reviewed
        if ProductReview.objects.filter(product=product, buyer=buyer).exists():
            return Response({'detail': 'You have already reviewed this product.'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Check if buyer has a COMPLETED order containing this product
        has_purchased = Order.objects.filter(
            buyer=buyer,
            status='PESANAN_SELESAI',
            items__product=product
        ).exists()
        
        if not has_purchased:
            return Response({'detail': 'You can only review products you have purchased and received.'}, status=status.HTTP_403_FORBIDDEN)
            
        # Create review
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product, buyer=buyer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
