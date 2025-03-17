from django.urls import path
from .views import WebsiteScannerAPIView

urlpatterns = [
    path('scan/', WebsiteScannerAPIView.as_view(), name='website-scan')
]