from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WebsiteViewSet,BlockedIPListAPIView,AutomationHistoryAPIView,loginAPI,RegisterAPIView,LogoutAPIView

router = DefaultRouter()
router.register(r'websites', WebsiteViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('blocked-ips/', BlockedIPListAPIView.as_view(), name='blocked-ip-list'),
    path('automation-history/', AutomationHistoryAPIView.as_view(), name='automation-history'),
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', loginAPI.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
]
