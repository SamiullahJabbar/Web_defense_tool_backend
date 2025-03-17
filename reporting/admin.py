from django.contrib import admin
from .models import DailyReport

@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'website', 'date', 'total_requests', 'anomalous_requests', 'blocked_ips_count', 'report_sent')
