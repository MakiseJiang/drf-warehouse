from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MaterialViewSet, TransactionViewSet, SystemSettingsViewSet


router = DefaultRouter()
router.register(r'materials', MaterialViewSet, basename='material')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'settings', SystemSettingsViewSet, basename='settings')

urlpatterns = [
    path('', include(router.urls)),
]