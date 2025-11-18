from rest_framework import serializers
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    """打卡记录序列化器"""
    
    task_title = serializers.CharField(source='task.title', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    task_score = serializers.IntegerField(source='task.score', read_only=True)
    
    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "description",
            "photo",
            "task",
            "task_title",
            "task_score",
            "team",
            "team_name",
        ]
        read_only_fields = ('id', 'task', 'team')


class PostCreateSerializer(serializers.ModelSerializer):
    """创建打卡记录序列化器"""
    
    class Meta:
        model = Post
        fields = [
            "title",
            "description",
            "photo",
            "task",
        ]
    
    def validate_title(self, value):
        """验证标题"""
        if not value or not value.strip():
            raise serializers.ValidationError("标题不能为空")
        if len(value) > 50:
            raise serializers.ValidationError("标题不能超过50个字符")
        return value.strip()
    
    def validate_description(self, value):
        """验证描述"""
        if value and len(value) > 500:
            raise serializers.ValidationError("描述不能超过500个字符")
        return value.strip() if value else ""
    
    def validate_photo(self, value):
        """验证图片"""
        if not value:
            raise serializers.ValidationError("请上传打卡图片")
        
        # 检查文件大小（限制5MB）
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("图片大小不能超过5MB")
        
        # 检查文件类型
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp']
        if hasattr(value, 'content_type') and value.content_type not in allowed_types:
            raise serializers.ValidationError("只支持 JPG、PNG、WEBP 格式的图片")
        
        return value
