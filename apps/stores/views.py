from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.users.permissions import IsActiveSeller
from .models import Store
from .serializers import StoreSerializer

class MyStoreView(APIView):
    permission_classes = [IsAuthenticated, IsActiveSeller]

    def get(self, request):
        if not hasattr(request.user, 'seller_profile'):
            return Response({"detail": "User is not a seller."}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            store = request.user.seller_profile.store
            serializer = StoreSerializer(store)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Store.DoesNotExist:
            return Response({"detail": "Store not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        if not hasattr(request.user, 'seller_profile'):
            return Response({"detail": "User is not a seller."}, status=status.HTTP_403_FORBIDDEN)
            
        if hasattr(request.user.seller_profile, 'store'):
            return Response({"detail": "Store already exists. Use PUT/PATCH to update."}, status=status.HTTP_400_BAD_REQUEST)
            
        serializer = StoreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(seller=request.user.seller_profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def patch(self, request):
        if not hasattr(request.user, 'seller_profile'):
            return Response({"detail": "User is not a seller."}, status=status.HTTP_403_FORBIDDEN)
            
        try:
            store = request.user.seller_profile.store
        except Store.DoesNotExist:
            return Response({"detail": "Store not found."}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = StoreSerializer(store, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        return self.patch(request)

class PublicStoreListView(generics.ListAPIView):
    queryset = Store.objects.all().order_by('-created_at')
    serializer_class = StoreSerializer
    permission_classes = [AllowAny]

class PublicStoreDetailView(generics.RetrieveAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
