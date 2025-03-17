from django.db import models
from django.contrib.auth.models import User
from monitor.models import Website

class DailyReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    total_requests = models.IntegerField(default=0)
    anomalous_requests = models.IntegerField(default=0)
    blocked_ips_count = models.IntegerField(default=0)
    report_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Report for {self.website.url} on {self.date}"
