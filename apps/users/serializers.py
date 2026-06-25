from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from .models import User, UserRole, BuyerProfile, SellerProfile, DriverProfile

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    roles = serializers.ListField(
        child=serializers.ChoiceField(choices=[('BUYER', 'BUYER'), ('SELLER', 'SELLER'), ('DRIVER', 'DRIVER')]),
        write_only=True,
        allow_empty=False
    )
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'roles')

    @transaction.atomic
    def create(self, validated_data):
        roles_data = validated_data.pop('roles')
        # ensure unique roles
        roles_data = list(set(roles_data))

        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()

        # create roles and profiles
        for role in roles_data:
            UserRole.objects.create(user=user, role=role)
            if role == 'BUYER':
                BuyerProfile.objects.get_or_create(user=user)
            elif role == 'SELLER':
                SellerProfile.objects.get_or_create(user=user)
            elif role == 'DRIVER':
                DriverProfile.objects.get_or_create(user=user)

        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['user_id'] = str(user.id)
        token['username'] = user.username
        
        # Get user roles
        roles = list(user.roles.values_list('role', flat=True))
        token['roles'] = roles
        
        if len(roles) == 1:
            token['active_role'] = roles[0]
        else:
            token['active_role'] = ""

        return token

class UserProfileSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    financial_summaries = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'roles', 'financial_summaries')

    def get_roles(self, obj):
        return list(obj.roles.values_list('role', flat=True))

    def get_financial_summaries(self, obj):
        summaries = {}
        if hasattr(obj, 'buyer_profile'):
            summaries['wallet_balance'] = float(obj.buyer_profile.wallet_balance)
        if hasattr(obj, 'seller_profile'):
            # Placeholder for Seller income (will be introduced in later levels)
            summaries['seller_income'] = 0.00
        if hasattr(obj, 'driver_profile'):
            summaries['driver_earnings'] = float(obj.driver_profile.total_earnings)
        return summaries

class SelectRoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=[('BUYER', 'BUYER'), ('SELLER', 'SELLER'), ('DRIVER', 'DRIVER')])

class AddRoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=[('SELLER', 'SELLER'), ('DRIVER', 'DRIVER')])

class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

