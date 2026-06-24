from django.urls import path
from .views import (
    AdminDashboardView, AdminUsersView, AdminStoresView,
    AdminProductsView, AdminOrdersView, AdminDiscountsView, AdminDeliveryJobsView
)

urlpatterns = [
    path('dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('users/', AdminUsersView.as_view(), name='admin_users'),
    path('stores/', AdminStoresView.as_view(), name='admin_stores'),
    path('products/', AdminProductsView.as_view(), name='admin_products'),
    path('orders/', AdminOrdersView.as_view(), name='admin_orders'),
    path('discounts/', AdminDiscountsView.as_view(), name='admin_discounts'),
    path('deliveries/', AdminDeliveryJobsView.as_view(), name='admin_deliveries'),
]
