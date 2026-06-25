from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    RegisterSerializer, CustomTokenObtainPairSerializer, 
    UserProfileSerializer, SelectRoleSerializer, AddRoleSerializer, LogoutSerializer
)
from .models import UserRole, SellerProfile, DriverProfile
from apps.stores.models import Store

class RegisterView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        roles = list(user.roles.values_list('role', flat=True))
        
        return Response({
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "roles": roles
            }
        }, status=status.HTTP_201_CREATED)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class SelectRoleView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SelectRoleSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = serializer.validated_data['role']
        
        user = request.user
        roles = list(user.roles.values_list('role', flat=True))
        
        if role not in roles:
            return Response({"detail": f"User does not have '{role}' role."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate new token with active_role
        token = CustomTokenObtainPairSerializer.get_token(user)
        token['active_role'] = role
        
        return Response({
            'refresh': str(token),
            'access': str(token.access_token),
        }, status=status.HTTP_200_OK)

class AddRoleView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AddRoleSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = serializer.validated_data['role']
        
        user = request.user
        roles = list(user.roles.values_list('role', flat=True))
        
        if 'ADMIN' in roles:
            return Response({"detail": "Admin cannot add other roles."}, status=status.HTTP_400_BAD_REQUEST)
            
        if role in roles:
            return Response({"detail": f"User already has '{role}' role."}, status=status.HTTP_400_BAD_REQUEST)
        
        UserRole.objects.create(user=user, role=role)
        
        if role == 'SELLER':
            profile, _ = SellerProfile.objects.get_or_create(user=user)
            Store.objects.get_or_create(seller=profile, defaults={
                'name': f"Toko {user.username}",
                'slug': f"toko-{user.username}",
                'description': f"Toko resmi milik {user.username}"
            })
        elif role == 'DRIVER':
            DriverProfile.objects.get_or_create(user=user)
            
        # Generate new token with the new role active
        token = CustomTokenObtainPairSerializer.get_token(user)
        token['active_role'] = role
        
        return Response({
            'refresh': str(token),
            'access': str(token.access_token),
        }, status=status.HTTP_200_OK)

class UserProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        data = serializer.data
        
        # get active role from token payload
        auth = request.auth
        active_role = auth.payload.get('active_role', "") if auth else ""
        
        data['active_role'] = active_role
        return Response(data, status=status.HTTP_200_OK)

class LogoutView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = serializer.validated_data['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
