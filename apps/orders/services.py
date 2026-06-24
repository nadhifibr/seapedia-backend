from django.db import transaction
from django.utils import timezone
from apps.orders.models import Order, OrderStatusHistory
from apps.wallet.models import WalletTransaction

def process_overdue_orders():
    now = timezone.now()
    # Find active orders that are overdue and not yet refunded
    overdue_orders = Order.objects.filter(
        status__in=['SEDANG_DIKEMAS', 'MENUNGGU_PENGIRIM', 'SEDANG_DIKIRIM'],
        overdue_at__lt=now,
        is_refunded=False
    )

    processed_count = 0
    for order in overdue_orders:
        with transaction.atomic():
            # Lock the order to prevent race conditions
            order = Order.objects.select_for_update().get(id=order.id)
            
            # Double check conditions after lock
            if order.is_refunded or order.status not in ['SEDANG_DIKEMAS', 'MENUNGGU_PENGIRIM', 'SEDANG_DIKIRIM']:
                continue
                
            buyer = order.buyer
            
            # 1. Restore stock
            for item in order.items.all():
                if item.product:
                    product = item.product
                    product.stock += item.quantity
                    product.save()
            
            # 2. Refund wallet
            buyer.wallet_balance += order.total
            buyer.save()
            
            WalletTransaction.objects.create(
                buyer=buyer,
                type='REFUND',
                amount=order.total,
                description=f"Auto-refund for overdue order {str(order.id)[:8]}"
            )
            
            # 3. Mark as refunded and change status
            order.is_refunded = True
            order.status = 'DIKEMBALIKAN'
            order.save()
            
            # 4. Create history
            OrderStatusHistory.objects.create(
                order=order,
                status='DIKEMBALIKAN',
                note='Pesanan otomatis dibatalkan dan dikembalikan (Overdue SLA).'
            )
            
            # 5. Cancel Delivery Job if exists
            if hasattr(order, 'delivery_job'):
                job = order.delivery_job
                if job.status != 'DONE':
                    job.status = 'CANCELLED'
                    job.save()
                    
            processed_count += 1
            
    return processed_count
