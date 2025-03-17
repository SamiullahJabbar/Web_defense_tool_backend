from django.contrib import admin
from .models import Website, RequestLog, ThreatDetectionLog,BlockedIP,AutomationHistory

@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ('url', 'domain', 'ip_address', 'user', 'email', 'is_active', 'added_on')  
    search_fields = ('url', 'domain', 'ip_address', 'email')  

@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'website', 'method', 'path', 'timestamp', 'is_anomalous')
    search_fields = ('ip_address', 'path')

@admin.register(ThreatDetectionLog)
class ThreatDetectionLogAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'website', 'ml_score', 'detection_type', 'location', 'detected_on')



@admin.register(BlockedIP)
class BlockedIPAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'blocked_at', 'is_permanent', 'unblock_at')
    search_fields = ('ip_address',)



from django.apps import AppConfig

class MonitorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitor'

    def ready(self):
        from django_q.models import Schedule
        try:
            # Check if the schedule already exists
            if not Schedule.objects.filter(name='Daily ML Retrain + Unblock').exists():
                Schedule.objects.create(
                    name='Daily ML Retrain + Unblock',
                    func='monitor.tasks.run_daily_automation',
                    schedule_type=Schedule.DAILY,
                    repeats=-1  # Infinite repeats
                )
        except Exception as e:
            print(f"⚠ Django-Q schedule creation failed: {e}")
            
@admin.register(AutomationHistory)
class AutomationHistoryAdmin(admin.ModelAdmin):
    list_display = ('task_name', 'status', 'executed_at')
    search_fields = ('task_name', 'status')
