from django.urls import path
from .views import CartView, CartItemView, CartItemDetailView

urlpatterns = [
    path('', CartView.as_view(), name='cart-detail'),
    path('items/', CartItemView.as_view(), name='cart-items'),
    path('items/<uuid:id>/', CartItemDetailView.as_view(), name='cart-item-detail'),
]
