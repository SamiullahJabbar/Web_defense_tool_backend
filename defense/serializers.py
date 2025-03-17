from rest_framework import serializers
from .models import BlockedIP

class BlockedIPSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedIP
        fields = '__all__'
