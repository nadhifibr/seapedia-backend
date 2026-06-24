from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from apps.users.permissions import IsActiveAdmin
from rest_framework.pagination import PageNumberPagination
from django.utils.timezone import now

from apps.users.models import User, UserRole
from apps.stores.models import Store
from apps.products.models import Product
from apps.orders.models import Order
from apps.discounts.models import Discount
from apps.deliveries.models import DeliveryJob

from apps.orders.services import process_overdue_orders
from rest_framework import status
from datetime import timedelta
from django.db.models import F

from .serializers import (
    AdminUserSerializer, AdminStoreSerializer, AdminProductSerializer,
    AdminOrderSerializer, AdminDiscountSerializer, AdminDeliveryJobSerializer
)

class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        # We now rely on IsActiveAdmin for the token validation.
        # This keeps the legacy check just in case, but IsActiveAdmin is stricter.
        return request.user.is_authenticated and UserRole.objects.filter(user=request.user, role='ADMIN').exists()

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole, IsActiveAdmin]

    def get(self, request):
        user_count = User.objects.count()
        store_count = Store.objects.count()
        product_count = Product.objects.count()
        order_count = Order.objects.count()
        voucher_count = Discount.objects.count()
        delivery_job_count = DeliveryJob.objects.count()
        
        overdue_orders_count = Order.objects.filter(overdue_at__lt=now()).exclude(status='PESANAN_SELESAI').count()

        data = {
            'users': user_count,
            'stores': store_count,
            'products': product_count,
            'orders': order_count,
            'vouchers_promos': voucher_count,
            'delivery_jobs': delivery_job_count,
            'overdue_orders': overdue_orders_count,
        }
        
        return Response(data)

class AdminUsersView(ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminRole, IsActiveAdmin]
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = AdminUserSerializer
    pagination_class = StandardResultsSetPagination

class AdminStoresView(ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminRole, IsActiveAdmin]
    queryset = Store.objects.all().order_by('-created_at')
    serializer_class = AdminStoreSerializer
    pagination_class = StandardResultsSetPagination

class AdminProductsView(ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminRole, IsActiveAdmin]
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = AdminProductSerializer
    pagination_class = StandardResultsSetPagination

class AdminOrdersView(ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminRole, IsActiveAdmin]
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = AdminOrderSerializer
    pagination_class = StandardResultsSetPagination

class AdminDiscountsView(ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminRole, IsActiveAdmin]
    queryset = Discount.objects.all().order_by('-expires_at')
    serializer_class = AdminDiscountSerializer
    pagination_class = StandardResultsSetPagination

class AdminDeliveryJobsView(ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminRole, IsActiveAdmin]
    queryset = DeliveryJob.objects.all().order_by('-taken_at')
    serializer_class = AdminDeliveryJobSerializer
    pagination_class = StandardResultsSetPagination

class TriggerOverdueView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole, IsActiveAdmin]

    def post(self, request):
        count = process_overdue_orders()
        return Response({'detail': f'Successfully processed {count} overdue orders.'}, status=status.HTTP_200_OK)

class SimulateTimeView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole, IsActiveAdmin]

    def post(self, request):
        days = request.data.get('days', 1)
        # Shift overdue_at back by `days` to simulate time passing
        orders = Order.objects.filter(status__in=['SEDANG_DIKEMAS', 'MENUNGGU_PENGIRIM', 'SEDANG_DIKIRIM'], is_refunded=False)
        updated = orders.update(overdue_at=F('overdue_at') - timedelta(days=int(days)))
        
        return Response({'detail': f'Simulated {days} days passing. Affected {updated} active orders.'}, status=status.HTTP_200_OK)
