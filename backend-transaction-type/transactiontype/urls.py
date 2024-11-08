# wallet/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet  ,UserRegistrationView ,QRCodeListView, QRViewSet ,FiatAddressViewSet  ,TransactionValidationViewSet  ,QRValidationViewSet ,NumberTransactionValidationViewSet  ,FetchQRCodeView ,get_wallet_amount ,get_currency_icon


router = DefaultRouter()

router.register(r'wallet_transfer', TransactionViewSet, basename='wallet_transfer')  # Make sure the URL pattern is 'transactions'
router.register(r'qrcode', QRViewSet, basename='qrcode')
router.register(r'validation-qrcode', QRValidationViewSet, basename='validation-qrcode')
router.register(r'address-transfer', FiatAddressViewSet, basename='address-transfer')
router.register(r'validate-transaction', TransactionValidationViewSet, basename='validate-transaction')
router.register(r'transaction_validation', NumberTransactionValidationViewSet, basename='transaction_validation')



urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationView.as_view(), name='user_registration'),
    path('qr_code_list/', QRCodeListView.as_view(), name='qr_code_list'),

    path('fetch-qr-code/', FetchQRCodeView.as_view(), name='fetch_qr_code'),
    path('get-wallet-amount/', get_wallet_amount, name='get_wallet_amount'),
    path('get-currency-icon/', get_currency_icon, name='get-currency-icon'),
]
