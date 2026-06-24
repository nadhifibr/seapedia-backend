from django.urls import path
from .views import MyStoreView, PublicStoreListView, PublicStoreDetailView

urlpatterns = [
    path('my-store/', MyStoreView.as_view(), name='my_store'),
    path('', PublicStoreListView.as_view(), name='store_list'),
    path('<slug:slug>/', PublicStoreDetailView.as_view(), name='store_detail'),
]
