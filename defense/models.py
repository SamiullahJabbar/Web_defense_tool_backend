# from django.db import models
# from django.contrib.auth.models import User

# class BlockedIP(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
#     ip_address = models.GenericIPAddressField(unique=True)
#     blocked_until = models.DateTimeField(null=True, blank=True)
#     permanently_blocked = models.BooleanField(default=False)
#     reason = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.ip_address} - {'Permanent' if self.permanently_blocked else 'Temporary'}"
