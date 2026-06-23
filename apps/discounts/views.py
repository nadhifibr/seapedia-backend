from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from .models import Discount, Voucher, Promo
from .serializers import VoucherSerializer, PromoSerializer, DiscountSerializer

class VoucherViewSet(viewsets.ModelViewSet):
    queryset = Voucher.objects.all()
    serializer_class = VoucherSerializer
    permission_classes = [permissions.IsAdminUser]

class PromoViewSet(viewsets.ModelViewSet):
    queryset = Promo.objects.all()
    serializer_class = PromoSerializer
    permission_classes = [permissions.IsAdminUser]

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def validate_discount(request):
    code = request.query_params.get('code')
    if not code:
        return Response({'detail': 'Code is required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        discount = Discount.objects.get(code=code)
    except Discount.DoesNotExist:
        return Response({'detail': 'Invalid discount code.'}, status=status.HTTP_404_NOT_FOUND)
        
    if not discount.is_active:
        return Response({'detail': 'Discount code is inactive.'}, status=status.HTTP_400_BAD_REQUEST)
        
    if discount.expires_at < timezone.now():
        return Response({'detail': 'Discount code has expired.'}, status=status.HTTP_400_BAD_REQUEST)
        
    if discount.type == 'VOUCHER':
        voucher = discount.voucher
        if voucher.used_count >= voucher.max_usage:
            return Response({'detail': 'Voucher usage limit reached.'}, status=status.HTTP_400_BAD_REQUEST)
            
    # return the valid discount details
    return Response(DiscountSerializer(discount).data)
