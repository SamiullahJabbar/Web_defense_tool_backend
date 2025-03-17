from .models import Subscription
from django.utils import timezone

def is_paid_user(user):
    sub = Subscription.objects.filter(user=user, is_active=True).first()
    return sub and sub.plan_name == 'Pro' and (not sub.expires_on or sub.expires_on > timezone.now())
