from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppReviewViewSet

router = DefaultRouter()
router.register(r'', AppReviewViewSet, basename='reviews')

urlpatterns = [
    path('', include(router.urls)),
]
