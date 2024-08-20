# wallet/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, TransactionViewSet  ,UserRegistrationView ,QRCodeListView, QRViewSet ,FiatAddressViewSet


router = DefaultRouter()

router.register(r'projects', ProjectViewSet)
router.register(r'wallet_transfer', TransactionViewSet)  # Make sure the URL pattern is 'transactions'
router.register(r'qrcode', QRViewSet, basename='qrcode')
router.register(r'address-transfer', FiatAddressViewSet, basename='address-transfer')


urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationView.as_view(), name='user_registration'),
    path('qr_code_list/', QRCodeListView.as_view(), name='qr_code_list'),
]
