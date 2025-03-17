from django.db import models
from django.contrib.auth.models import User


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    plan_name = models.CharField(max_length=50, choices=[('Free', 'Free'), ('Pro', 'Pro')], default='Free')
    is_active = models.BooleanField(default=True)  # Free is always active
    subscribed_on = models.DateTimeField(auto_now_add=True)
    expires_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan_name}"