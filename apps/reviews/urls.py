from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppReviewViewSet, ProductReviewListCreateView

router = DefaultRouter()
router.register(r'', AppReviewViewSet, basename='reviews')

urlpatterns = [
    path('', include(router.urls)),
    path('product/<uuid:product_id>/', ProductReviewListCreateView.as_view(), name='product-reviews'),
]
