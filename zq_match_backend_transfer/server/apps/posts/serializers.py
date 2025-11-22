from rest_framework import serializers
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    """打卡记录序列化器"""
    
    task_title = serializers.CharField(source='task.title', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    task_score = serializers.IntegerField(source='task.score', read_only=True)
    photo = serializers.SerializerMethodField()
    
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
    
    def get_photo(self, obj):
        """获取图片URL，修正路径错误"""
        if not obj.photo:
            return None
        
        # 获取request对象（用于构建完整URL）
        request = self.context.get('request')
        
        # 获取photo路径
        photo_path = obj.photo.name if hasattr(obj.photo, 'name') else str(obj.photo)
        
        # 修正路径：如果路径中包含checkin/，替换为post/photo/
        if 'checkin/' in photo_path:
            # 提取文件名
            filename = photo_path.split('checkin/')[-1]
            photo_path = f"post/photo/{filename}"
        
        # 构建URL
        from django.conf import settings
        url_path = photo_path.replace('\\', '/')  # Windows路径转URL路径
        if not url_path.startswith('/'):
            url_path = '/' + url_path
        media_url = settings.MEDIA_URL.rstrip('/')
        
        if request:
            # 使用request构建完整URL
            return request.build_absolute_uri(f"{media_url}{url_path}")
        else:
            # 没有request时，返回相对路径
            return f"{media_url}{url_path}"


class PostCreateSerializer(serializers.ModelSerializer):
    """创建打卡记录序列化器"""
    is_published = serializers.BooleanField(required=False, default=False)
    
    class Meta:
        model = Post
        fields = [
            "title",
            "description",
            "photo",
            "task",
            "is_published",
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
