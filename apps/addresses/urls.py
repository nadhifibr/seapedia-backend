from django.urls import path
from .views import DeliveryAddressListCreateView, DeliveryAddressDetailView

urlpatterns = [
    path('', DeliveryAddressListCreateView.as_view(), name='address-list-create'),
    path('<uuid:id>/', DeliveryAddressDetailView.as_view(), name='address-detail'),
]
