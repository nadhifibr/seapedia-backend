from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VoucherViewSet, PromoViewSet, validate_discount

router = DefaultRouter()
router.register(r'admin/vouchers', VoucherViewSet, basename='admin-voucher')
router.register(r'admin/promos', PromoViewSet, basename='admin-promo')

urlpatterns = [
    path('validate/', validate_discount, name='validate-discount'),
    path('', include(router.urls)),
]
