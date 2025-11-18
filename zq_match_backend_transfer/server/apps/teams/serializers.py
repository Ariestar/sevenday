from rest_framework import serializers
from users.serializers import UserSerializer
from tasks.serializers import TaskSerializer
from .models import Team


class TeamInfoSerializer(serializers.ModelSerializer):
    """队伍详细信息序列化器（包含成员和任务信息）"""
    
    members = serializers.SerializerMethodField()
    completed_tasks = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = [
            "id",
            "name",
            "introduction",
            "score",
            "members",
            "completed_tasks",
        ]
    
    def get_members(self, obj):
        """获取队伍成员"""
        from users.models import User
        users = User.objects.filter(team=obj)
        return UserSerializer(users, many=True).data
    
    def get_completed_tasks(self, obj):
        """获取已完成的任务"""
        return TaskSerializer(obj.task.all(), many=True).data


class TeamSerializer(serializers.ModelSerializer):
    """队伍基本序列化器（用于更新）"""
    
    class Meta:
        model = Team
        fields = [
            "id",
            "name",
            "introduction",
        ]
        read_only_fields = ('id',)
    
    def validate_name(self, value):
        """验证队伍名称"""
        if len(value) > 30:
            raise serializers.ValidationError("队伍名称不能超过30个字符")
        return value
