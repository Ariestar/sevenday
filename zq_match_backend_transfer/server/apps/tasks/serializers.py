from rest_framework import serializers
from django.utils import timezone
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    """任务序列化器"""
    
    is_active = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "cover",
            "introduction",
            "score",
            "start_time",
            "end_time",
            "is_active",
            "is_expired",
            "create_time",
            "update_time",
        ]
        read_only_fields = ('id', 'create_time', 'update_time')
    
    def get_is_active(self, obj):
        """任务是否进行中"""
        now = timezone.now().date()
        return obj.start_time <= now <= obj.end_time
    
    def get_is_expired(self, obj):
        """任务是否已过期"""
        now = timezone.now().date()
        return now > obj.end_time
    
    def validate(self, attrs):
        """验证时间范围"""
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        
        if start_time and end_time and start_time > end_time:
            raise serializers.ValidationError("开始时间不能晚于结束时间")
        
        return attrs
