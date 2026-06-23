from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, SellerOrderViewSet

seller_router = DefaultRouter()
seller_router.register(r'incoming', SellerOrderViewSet, basename='seller-order')

urlpatterns = [
    # Seller endpoints (via router)
    path('', include(seller_router.urls)),
    
    # Buyer endpoints (manual wiring to avoid empty-prefix router bugs)
    path('checkout-summary/', OrderViewSet.as_view({'get': 'checkout_summary', 'post': 'checkout_summary'}), name='order-checkout-summary'),
    path('checkout/', OrderViewSet.as_view({'post': 'checkout'}), name='order-checkout'),
    path('', OrderViewSet.as_view({'get': 'list'}), name='order-list'),
    path('<uuid:pk>/', OrderViewSet.as_view({'get': 'retrieve'}), name='order-detail'),
]
