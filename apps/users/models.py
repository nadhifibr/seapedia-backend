import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError

class CustomUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        user = super().create_superuser(username, email, password, **extra_fields)
        # Otomatis menambahkan role ADMIN ke UserRole
        from apps.users.models import UserRole
        UserRole.objects.get_or_create(user=user, role='ADMIN')
        return user

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(
        max_length=150, 
        unique=True, 
        validators=[UnicodeUsernameValidator()],
        error_messages={'unique': "A user with that username already exists."}
    )
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = CustomUserManager()

class UserRole(models.Model):
    ROLE_CHOICES = [
        ('BUYER', 'Buyer'),
        ('SELLER', 'Seller'),
        ('DRIVER', 'Driver'),
        ('ADMIN', 'Admin'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roles')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'role')

    def clean(self):
        super().clean()
        
        # Admin restriction
        if getattr(self, 'user', None):
            existing_roles = self.user.roles.exclude(id=self.id).values_list('role', flat=True)
            
            if self.role == 'ADMIN' and existing_roles:
                raise ValidationError("Admin tidak boleh memiliki role lain. User ini sudah memiliki role: " + ", ".join(existing_roles))
            
            if self.role != 'ADMIN' and 'ADMIN' in existing_roles:
                raise ValidationError("User dengan role Admin tidak boleh ditambah role lain.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class BuyerProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='buyer_profile')
    wallet_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

class SellerProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')

class DriverProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_profile')
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
