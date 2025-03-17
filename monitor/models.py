from django.db import models
from django.contrib.auth.models import User


class Website(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    url = models.URLField()
    domain = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    email = models.EmailField(null=True, blank=True) 
    is_active = models.BooleanField(default=True)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.url


class RequestLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(blank=True, null=True)
    anomaly_score = models.FloatField(default=0.0)
    is_anomalous = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.ip_address} - {self.path}"

class ThreatDetectionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    ml_score = models.FloatField()
    detection_type = models.CharField(max_length=100)
    location = models.CharField(max_length=255, blank=True, null=True)
    detected_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ip_address} - {self.detection_type}"





class BlockedIP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    website = models.ForeignKey(Website, on_delete=models.CASCADE, null=True, blank=True) 
    ip_address = models.GenericIPAddressField(unique=True)
    blocked_at = models.DateTimeField(auto_now_add=True)
    block_reason = models.TextField()
    is_permanent = models.BooleanField(default=False)
    unblock_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.ip_address



class AutomationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    task_name = models.CharField(max_length=255)
    status = models.CharField(max_length=50) 
    message = models.TextField(null=True, blank=True)
    executed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task_name} - {self.status} at {self.executed_at}"
