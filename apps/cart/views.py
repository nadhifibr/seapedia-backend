from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.db import transaction
from .models import Cart, CartItem
from apps.products.models import Product
from .serializers import CartSerializer, CartItemSerializer
from apps.users.models import BuyerProfile

class BuyerPermissionMixin:
    permission_classes = [IsAuthenticated]
    
    def get_buyer_profile(self, user):
        if not user.roles.filter(role='BUYER').exists():
            raise PermissionDenied("Only buyers can use the cart.")
        try:
            return user.buyer_profile
        except BuyerProfile.DoesNotExist:
            raise PermissionDenied("Buyer profile not found.")

class CartView(BuyerPermissionMixin, APIView):
    def get(self, request):
        buyer = self.get_buyer_profile(request.user)
        cart, created = Cart.objects.get_or_create(buyer=buyer)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def delete(self, request):
        buyer = self.get_buyer_profile(request.user)
        cart, created = Cart.objects.get_or_create(buyer=buyer)
        cart.items.all().delete()
        cart.store = None
        cart.save()
        return Response({'detail': 'Cart cleared'}, status=status.HTTP_200_OK)

class CartItemView(BuyerPermissionMixin, APIView):
    def post(self, request):
        buyer = self.get_buyer_profile(request.user)
        cart, created = Cart.objects.get_or_create(buyer=buyer)
        
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
            
        if product.stock < quantity:
            return Response({'detail': 'Not enough stock'}, status=status.HTTP_400_BAD_REQUEST)

        # Single store validation
        if cart.store and cart.store != product.store:
            return Response({
                'error_code': 'STORE_CONFLICT',
                'detail': f'Cart already contains items from {cart.store.name}. Cannot add items from {product.store.name}.'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        with transaction.atomic():
            if not cart.store:
                cart.store = product.store
                cart.save()
                
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, 
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                if cart_item.quantity + quantity > product.stock:
                    return Response({'detail': 'Not enough stock for total quantity'}, status=status.HTTP_400_BAD_REQUEST)
                cart_item.quantity += quantity
                cart_item.save()
                
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

class CartItemDetailView(BuyerPermissionMixin, APIView):
    def patch(self, request, id):
        buyer = self.get_buyer_profile(request.user)
        try:
            item = CartItem.objects.get(id=id, cart__buyer=buyer)
        except CartItem.DoesNotExist:
            return Response({'detail': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
            
        quantity = int(request.data.get('quantity', item.quantity))
        if quantity <= 0:
            return self.delete(request, id)
            
        if quantity > item.product.stock:
            return Response({'detail': 'Not enough stock'}, status=status.HTTP_400_BAD_REQUEST)
            
        item.quantity = quantity
        item.save()
        return Response(CartItemSerializer(item).data)

    def delete(self, request, id):
        buyer = self.get_buyer_profile(request.user)
        try:
            item = CartItem.objects.get(id=id, cart__buyer=buyer)
            cart = item.cart
            item.delete()
            
            # If cart is empty, unset the store
            if not cart.items.exists():
                cart.store = None
                cart.save()
                
            return Response({'detail': 'Item deleted'}, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({'detail': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
