from django.urls import path
from .views import WalletBalanceView, WalletTransactionListView, TopupWalletView

urlpatterns = [
    path('balance/', WalletBalanceView.as_view(), name='wallet-balance'),
    path('transactions/', WalletTransactionListView.as_view(), name='wallet-transactions'),
    path('topup/', TopupWalletView.as_view(), name='wallet-topup'),
]
