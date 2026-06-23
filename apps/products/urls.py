from django.urls import path
from .views import (
    SellerProductListCreateView, 
    SellerProductDetailView,
    PublicProductListView,
    PublicProductDetailView
)

urlpatterns = [
    path('', PublicProductListView.as_view(), name='public_product_list'),
    path('<uuid:pk>/', PublicProductDetailView.as_view(), name='public_product_detail'),
    path('my-products/', SellerProductListCreateView.as_view(), name='seller_product_list_create'),
    path('my-products/<uuid:pk>/', SellerProductDetailView.as_view(), name='seller_product_detail'),
]
