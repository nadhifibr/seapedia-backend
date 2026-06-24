from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import IsActiveDriver
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from .models import DeliveryJob
from .serializers import DeliveryJobSerializer
from apps.orders.models import OrderStatusHistory

class DeliveryJobViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsActiveDriver]
    serializer_class = DeliveryJobSerializer

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'driver_profile'):
            return DeliveryJob.objects.none()
            
        # Show jobs that are available OR belong to the current driver
        available_jobs = DeliveryJob.objects.filter(status='AVAILABLE')
        
        # Multirole Protection: Don't show jobs where the driver is the buyer or the seller
        if hasattr(user, 'buyer_profile'):
            available_jobs = available_jobs.exclude(order__buyer=user.buyer_profile)
        if hasattr(user, 'seller_profile') and hasattr(user.seller_profile, 'store'):
            available_jobs = available_jobs.exclude(order__store=user.seller_profile.store)
            
        my_jobs = DeliveryJob.objects.filter(driver=user.driver_profile)
        
        return (available_jobs | my_jobs).order_by('-order__created_at')

    @action(detail=True, methods=['post'], url_path='take')
    def take_job(self, request, pk=None):
        user = request.user
        if not hasattr(user, 'driver_profile'):
            return Response({'detail': 'Not a driver.'}, status=status.HTTP_403_FORBIDDEN)
            
        driver = user.driver_profile
        
        with transaction.atomic():
            job = DeliveryJob.objects.select_for_update().get(pk=pk)
            
            if job.status != 'AVAILABLE':
                return Response({'detail': 'Job is no longer available.'}, status=status.HTTP_400_BAD_REQUEST)
                
            if job.order.status != 'MENUNGGU_PENGIRIM':
                return Response({'detail': 'Order is not ready for delivery.'}, status=status.HTTP_400_BAD_REQUEST)
                
            # Multirole Protection Validation
            if hasattr(user, 'buyer_profile') and job.order.buyer == user.buyer_profile:
                return Response({'detail': 'You cannot deliver your own orders.'}, status=status.HTTP_400_BAD_REQUEST)
            if hasattr(user, 'seller_profile') and hasattr(user.seller_profile, 'store') and job.order.store == user.seller_profile.store:
                return Response({'detail': 'You cannot deliver orders from your own store.'}, status=status.HTTP_400_BAD_REQUEST)
                
            # Update Job
            job.status = 'TAKEN'
            job.driver = driver
            job.taken_at = timezone.now()
            job.save()
            
            # Update Order
            order = job.order
            order.status = 'SEDANG_DIKIRIM'
            order.save()
            
            # Track History
            OrderStatusHistory.objects.create(
                order=order,
                status='SEDANG_DIKIRIM',
                note='Pesanan sedang diantar oleh kurir.'
            )
            
        return Response(DeliveryJobSerializer(job).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='complete')
    def complete_job(self, request, pk=None):
        user = request.user
        if not hasattr(user, 'driver_profile'):
            return Response({'detail': 'Not a driver.'}, status=status.HTTP_403_FORBIDDEN)
            
        driver = user.driver_profile
        
        with transaction.atomic():
            job = DeliveryJob.objects.select_for_update().get(pk=pk)
            
            if job.status != 'TAKEN' or job.driver != driver:
                return Response({'detail': 'You are not assigned to this job.'}, status=status.HTTP_400_BAD_REQUEST)
                
            if job.order.status != 'SEDANG_DIKIRIM':
                return Response({'detail': 'Order is not currently in transit.'}, status=status.HTTP_400_BAD_REQUEST)
                
            # Update Job
            job.status = 'DONE'
            job.completed_at = timezone.now()
            job.save()
            
            # Update Order
            order = job.order
            order.status = 'PESANAN_SELESAI'
            order.save()
            
            # Track History
            OrderStatusHistory.objects.create(
                order=order,
                status='PESANAN_SELESAI',
                note='Pesanan telah sampai dan selesai.'
            )
            
            # Add Earnings to Driver Profile
            driver.total_earnings += job.driver_earning
            driver.save()
            
        return Response(DeliveryJobSerializer(job).data, status=status.HTTP_200_OK)
