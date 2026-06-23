from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.db.models import Sum, F
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem, OrderStatusHistory
from .serializers import OrderSerializer, CheckoutSummarySerializer, CheckoutSerializer
from apps.cart.models import CartItem
from apps.addresses.models import DeliveryAddress
from apps.wallet.models import WalletTransaction
from decimal import Decimal
from django.utils import timezone
from apps.discounts.models import Discount
from apps.deliveries.models import DeliveryJob

def calculate_discount_amount(discount, subtotal):
    if not discount or not discount.is_active or discount.expires_at < timezone.now():
        return Decimal('0.00'), None
        
    if discount.type == 'VOUCHER':
        voucher = getattr(discount, 'voucher', None)
        if voucher and voucher.used_count >= voucher.max_usage:
            return Decimal('0.00'), None
            
    amount = Decimal('0.00')
    if discount.value_type == 'PERCENT':
        amount = subtotal * (discount.value / Decimal('100.00'))
    else:
        amount = discount.value
        
    if amount > subtotal:
        amount = subtotal
        
    return amount.quantize(Decimal('0.00')), discount
DELIVERY_FEES = {
    'INSTANT': Decimal('50000.00'),
    'NEXT_DAY': Decimal('20000.00'),
    'REGULAR': Decimal('10000.00'),
}

class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'buyer_profile'):
            return Order.objects.filter(buyer=user.buyer_profile).order_by('-created_at')
        return Order.objects.none()

    @action(detail=False, methods=['get'])
    def report(self, request):
        user = self.request.user
        if not hasattr(user, 'buyer_profile'):
            return Response({'detail': 'Not a buyer.'}, status=status.HTTP_400_BAD_REQUEST)
            
        orders = Order.objects.filter(buyer=user.buyer_profile, is_refunded=False)
        total_spent = orders.aggregate(total_sum=Sum('total'))['total_sum'] or Decimal('0.00')
        total_orders = orders.count()
        
        return Response({
            'total_spent': total_spent,
            'total_orders': total_orders
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post', 'get'], url_path='checkout-summary')
    def checkout_summary(self, request):
        if request.method == 'GET':
            # Support params from query for GET
            delivery_method = request.query_params.get('delivery_method', 'REGULAR')
            address_id = request.query_params.get('address_id')
            discount_code = request.query_params.get('discount_code')
        else:
            serializer = CheckoutSummarySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            delivery_method = serializer.validated_data['delivery_method']
            address_id = serializer.validated_data.get('address_id')
            discount_code = serializer.validated_data.get('discount_code')

        user = request.user
        try:
            buyer = user.buyer_profile
        except AttributeError:
            return Response({'detail': 'Not a buyer.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            cart = buyer.cart
        except AttributeError:
            return Response({'detail': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        cart_items = cart.items.all()
        if not cart_items.exists() or not cart.store:
            return Response({'detail': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        subtotal = sum((item.product.price * item.quantity) for item in cart_items)
        
        discount_amount = Decimal('0.00')
        applied_discount = None
        if discount_code:
            discount = Discount.objects.filter(code=discount_code).first()
            discount_amount, applied_discount = calculate_discount_amount(discount, subtotal)
            
        delivery_fee = DELIVERY_FEES.get(delivery_method, Decimal('0.00'))
        tax_amount = ((subtotal - discount_amount) * Decimal('0.12')).quantize(Decimal('0.00'))
        total = (subtotal - discount_amount) + delivery_fee + tax_amount

        # Find address
        address = None
        if address_id:
            address = DeliveryAddress.objects.filter(id=address_id, buyer=buyer).first()
        if not address:
            address = DeliveryAddress.objects.filter(buyer=buyer, is_default=True).first()
        
        address_info = None
        if address:
            address_info = {
                'id': address.id,
                'label': address.label,
                'full_address': address.full_address
            }

        items_data = []
        for item in cart_items:
            items_data.append({
                'product_id': item.product.id,
                'product_name': item.product.name,
                'price': item.product.price,
                'quantity': item.quantity,
                'image_url': item.product.image_url,
            })

        return Response({
            'items': items_data,
            'subtotal': subtotal,
            'discount_amount': discount_amount,
            'discount_type': applied_discount.type if applied_discount else None,
            'delivery_fee': delivery_fee,
            'tax_amount': tax_amount,
            'total': total,
            'delivery_method': delivery_method,
            'address': address_info,
            'store_id': cart.store.id,
            'store_name': cart.store.name,
        })

    @action(detail=False, methods=['post'], url_path='checkout')
    def checkout(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        delivery_method = serializer.validated_data['delivery_method']
        address_id = serializer.validated_data['address_id']
        discount_code = serializer.validated_data.get('discount_code')

        user = request.user
        try:
            buyer = user.buyer_profile
        except AttributeError:
            return Response({'detail': 'Not a buyer.'}, status=status.HTTP_403_FORBIDDEN)

        address = get_object_or_404(DeliveryAddress, id=address_id, buyer=buyer)
        address_snapshot = f"{address.label} - {address.full_address}"

        try:
            cart = buyer.cart
        except AttributeError:
            return Response({'detail': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        cart_items = cart.items.all()
        if not cart_items.exists() or not cart.store:
            return Response({'detail': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Re-fetch for update to avoid race conditions
            cart_items_qs = CartItem.objects.select_related('product').filter(cart=cart).select_for_update()
            cart_items_list = list(cart_items_qs)
            
            subtotal = sum((item.product.price * item.quantity) for item in cart_items_list)
            
            discount_amount = Decimal('0.00')
            applied_discount = None
            if discount_code:
                discount = Discount.objects.filter(code=discount_code).first()
                discount_amount, applied_discount = calculate_discount_amount(discount, subtotal)
                
                if not applied_discount:
                     return Response({'detail': 'Invalid or expired discount code.'}, status=status.HTTP_400_BAD_REQUEST)
                
            delivery_fee = DELIVERY_FEES.get(delivery_method, Decimal('0.00'))
            tax_amount = ((subtotal - discount_amount) * Decimal('0.12')).quantize(Decimal('0.00'))
            total = (subtotal - discount_amount) + delivery_fee + tax_amount

            # Check wallet balance
            if buyer.wallet_balance < total:
                return Response({'detail': 'Insufficient wallet balance.'}, status=status.HTTP_400_BAD_REQUEST)

            # Check and reduce stock
            for item in cart_items_list:
                if item.product.stock < item.quantity:
                    return Response({'detail': f'Insufficient stock for {item.product.name}.'}, status=status.HTTP_400_BAD_REQUEST)
                item.product.stock -= item.quantity
                item.product.save()
                
            # Increment voucher usage if applicable
            if applied_discount and applied_discount.type == 'VOUCHER':
                from apps.discounts.models import Voucher
                voucher = Voucher.objects.select_for_update().get(id=applied_discount.voucher.id)
                voucher.used_count += 1
                voucher.save()

            # Deduct wallet
            buyer.wallet_balance -= total
            buyer.save()

            WalletTransaction.objects.create(
                buyer=buyer,
                type='PAYMENT',
                amount=total,
                description=f"Payment for checkout"
            )

            # Create Order
            order = Order.objects.create(
                buyer=buyer,
                store=cart.store,
                discount=applied_discount,
                delivery_method=delivery_method,
                address_snapshot=address_snapshot,
                subtotal=subtotal,
                discount_amount=discount_amount,
                delivery_fee=delivery_fee,
                tax_amount=tax_amount,
                total=total,
                status='SEDANG_DIKEMAS'
            )

            # Create OrderItems
            for item in cart_items_list:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    price_snapshot=item.product.price,
                    quantity=item.quantity
                )

            # Create OrderStatusHistory
            OrderStatusHistory.objects.create(
                order=order,
                status='SEDANG_DIKEMAS',
                note='Order placed successfully.'
            )

            # Clear cart
            cart.items.all().delete()
            cart.store = None
            cart.save()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

class SellerOrderViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'seller_profile') and hasattr(user.seller_profile, 'store'):
            return Order.objects.filter(store=user.seller_profile.store).order_by('-created_at')
        return Order.objects.none()

    @action(detail=False, methods=['get'])
    def report(self, request):
        user = self.request.user
        if not hasattr(user, 'seller_profile') or not hasattr(user.seller_profile, 'store'):
            return Response({'detail': 'Not a seller or no store.'}, status=status.HTTP_400_BAD_REQUEST)
            
        orders = Order.objects.filter(store=user.seller_profile.store, is_refunded=False)
        revenue = orders.aggregate(
            total_revenue=Sum(F('subtotal') - F('discount_amount'))
        )['total_revenue'] or Decimal('0.00')
        total_orders = orders.count()
        
        return Response({
            'total_revenue': revenue,
            'total_orders': total_orders
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='process')
    def process_order(self, request, pk=None):
        order = self.get_object()
        
        if order.status != 'SEDANG_DIKEMAS':
            return Response({'detail': 'Only orders with SEDANG_DIKEMAS status can be processed.'}, status=status.HTTP_400_BAD_REQUEST)
            
        with transaction.atomic():
            order.status = 'MENUNGGU_PENGIRIM'
            order.save()
            
            OrderStatusHistory.objects.create(
                order=order,
                status='MENUNGGU_PENGIRIM',
                note='Pesanan telah diproses oleh penjual dan menunggu pengiriman.'
            )
            
            DeliveryJob.objects.create(
                order=order,
                status='AVAILABLE',
                driver_earning=order.delivery_fee
            )
            
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
