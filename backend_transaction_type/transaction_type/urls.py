# wallet/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, TransactionViewSet ,WalletViewSet,AddressViewSet,AddressBasedTransactionViewSet ,UserRegistrationView ,QRCodeListView


router = DefaultRouter()

router.register(r'projects', ProjectViewSet)
router.register(r'wallets', WalletViewSet)
router.register(r'wallet_transfer', TransactionViewSet)  # Make sure the URL pattern is 'transactions'

router.register(r'address', AddressViewSet)
router.register(r'address_based_transfer', AddressBasedTransactionViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationView.as_view(), name='user_registration'),
    path('qr_code_list/', QRCodeListView.as_view(), name='qr_code_list'),
]
