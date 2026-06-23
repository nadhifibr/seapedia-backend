from django.urls import path
from .views import SellerProductListCreateView, SellerProductDetailView

urlpatterns = [
    path('my-products/', SellerProductListCreateView.as_view(), name='seller_product_list_create'),
    path('my-products/<uuid:pk>/', SellerProductDetailView.as_view(), name='seller_product_detail'),
]
