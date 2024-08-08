# wallet/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, TransactionViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'wallet_transfer', TransactionViewSet)  # Make sure the URL pattern is 'transactions'

urlpatterns = [
    path('', include(router.urls)),
]
