from rest_framework import serializers
from .models import Website, RequestLog, ThreatDetectionLog

class WebsiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        fields = '__all__'

class RequestLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestLog
        fields = '__all__'

class ThreatDetectionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThreatDetectionLog
        fields = '__all__'
