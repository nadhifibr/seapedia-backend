from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.pagination import PageNumberPagination
from django.utils.timezone import now

from apps.users.models import User, UserRole
from apps.stores.models import Store
from apps.products.models import Product
from apps.orders.models import Order
from apps.discounts.models import Discount
from apps.deliveries.models import DeliveryJob

from .serializers import (
    AdminUserSerializer, AdminStoreSerializer, AdminProductSerializer,
    AdminOrderSerializer, AdminDiscountSerializer, AdminDeliveryJobSerializer
)

class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and UserRole.objects.filter(user=request.user, role='ADMIN').exists()

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

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
    permission_classes = [IsAuthenticated, IsAdminRole]
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = AdminUserSerializer
    pagination_class = StandardResultsSetPagination

class AdminStoresView(ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    queryset = Store.objects.all().order_by('-created_at')
    serializer_class = AdminStoreSerializer
    pagination_class = StandardResultsSetPagination

class AdminProductsView(ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = AdminProductSerializer
    pagination_class = StandardResultsSetPagination

class AdminOrdersView(ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = AdminOrderSerializer
    pagination_class = StandardResultsSetPagination

class AdminDiscountsView(ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    queryset = Discount.objects.all().order_by('-expires_at')
    serializer_class = AdminDiscountSerializer
    pagination_class = StandardResultsSetPagination

class AdminDeliveryJobsView(ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    queryset = DeliveryJob.objects.all().order_by('-taken_at')
    serializer_class = AdminDeliveryJobSerializer
    pagination_class = StandardResultsSetPagination
