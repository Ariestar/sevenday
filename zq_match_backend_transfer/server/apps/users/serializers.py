from rest_framework import serializers
from zq_django_util.exceptions import ApiException
from zq_django_util.response import ResponseType

from server.utils.images import validate_image, compress_image
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """用户详细信息序列化器"""
    
    academy_name = serializers.CharField(source='academy.name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "qq",
            "wechat",
            "school_number",
            "avatar",
            "gender",
            "academy",
            "academy_name",
            "grade",
            "interest",
            "is_match",
            "team",
            "team_name",
        ]
        read_only_fields = ('id', 'email', 'is_match', 'team')

    def validate_username(self, value):
        """验证用户名"""
        if len(value) > 20:
            raise serializers.ValidationError("用户名不能超过20个字符")
        if len(value) < 2:
            raise serializers.ValidationError("用户名至少需要2个字符")
        return value
    
    def validate_phone(self, value):
        """验证手机号"""
        import re
        if value and not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError("手机号格式不正确")
        return value
    
    def validate_qq(self, value):
        """验证QQ号"""
        import re
        if value and not re.match(r'^\d{5,16}$', value):
            raise serializers.ValidationError("QQ号格式不正确")
        return value

    def validate_avatar(self, value):
        """检查并压缩头像"""
        if value:
            value = validate_image(
                value,
                max_size=1024 * 1024 * 4,
            )
            value = compress_image(value, "avatar", width=300)
        return value


class UserInfoSerializer(serializers.ModelSerializer):
    """用户基本信息序列化器（用于展示）"""
    
    academy_name = serializers.CharField(source='academy.name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "avatar",
            "gender",
            "academy",
            "academy_name",
            "grade",
            "interest",
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """修改密码序列化器"""
    
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)
    
    def validate_new_password(self, value):
        """验证新密码强度"""
        if len(value) < 8:
            raise serializers.ValidationError("密码至少需要8个字符")
        return value
