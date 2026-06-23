from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import WalletTransaction
from .serializers import WalletTransactionSerializer, TopupSerializer
from apps.users.models import BuyerProfile

class BuyerPermissionMixin:
    permission_classes = [IsAuthenticated]
    
    def get_buyer_profile(self, user):
        if not user.roles or 'BUYER' not in user.roles:
            return None
        try:
            return user.buyer_profile
        except BuyerProfile.DoesNotExist:
            return None

class WalletBalanceView(BuyerPermissionMixin, APIView):
    def get(self, request):
        buyer = self.get_buyer_profile(request.user)
        if not buyer:
            return Response({'detail': 'Only buyers have a wallet.'}, status=status.HTTP_403_FORBIDDEN)
        
        return Response({'balance': buyer.wallet_balance})

class WalletTransactionListView(BuyerPermissionMixin, generics.ListAPIView):
    serializer_class = WalletTransactionSerializer
    
    def get_queryset(self):
        buyer = self.get_buyer_profile(self.request.user)
        if not buyer:
            return WalletTransaction.objects.none()
        return WalletTransaction.objects.filter(buyer=buyer).order_by('-created_at')

class TopupWalletView(BuyerPermissionMixin, APIView):
    def post(self, request):
        buyer = self.get_buyer_profile(request.user)
        if not buyer:
            return Response({'detail': 'Only buyers can top up.'}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = TopupSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            with transaction.atomic():
                buyer.wallet_balance += amount
                buyer.save()
                
                # Create transaction record
                WalletTransaction.objects.create(
                    buyer=buyer,
                    type='TOPUP',
                    amount=amount,
                    description=f'Dummy top-up of ${amount}'
                )
            return Response({
                'detail': 'Top-up successful',
                'new_balance': buyer.wallet_balance
            }, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
