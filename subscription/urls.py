from django.urls import path
from .views import CreateStripeCheckoutSessionAPIView, stripe_webhook_view,SubscriptionStatusAPIView,WebsiteLinkAPIView,ScanUsageLogsAPIView,DashboardSummaryAPIView,StripeSuccessRedirectView,VerifyPaymentAPIView

urlpatterns = [
    path('create-checkout-session', CreateStripeCheckoutSessionAPIView.as_view(), name='create-checkout-session'),
    path('verify-payment', VerifyPaymentAPIView.as_view(), name='verify-payment'),
    path('stripe-webhook/', stripe_webhook_view, name='stripe-webhook'),
    path('subscription-status/', SubscriptionStatusAPIView.as_view(), name='subscription-status'),
    path('link-website/', WebsiteLinkAPIView.as_view(), name='link-website'),
    path('scan-usage-logs/', ScanUsageLogsAPIView.as_view(), name='scan-usage-logs'),
    path('dashboard-summary/', DashboardSummaryAPIView.as_view(), name='dashboard-summary'),
    path('subscription-success/', StripeSuccessRedirectView.as_view(), name='subscription-success'),
]
