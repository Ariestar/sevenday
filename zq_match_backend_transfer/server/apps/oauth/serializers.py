from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from oauth.backends import UnionIdBackend
from rest_framework import serializers
from rest_framework_simplejwt.serializers import PasswordField
from users.models import User
from zq_auth_sdk import UserNotFoundException
from zq_django_util.exceptions import ApiException
from zq_django_util.response import ResponseType
from zq_django_util.utils.auth.backends import OpenIdBackend
from zq_django_util.utils.auth.serializers import (
    OpenIdLoginSerializer as DefaultOpenIdLoginSerializer,
)

import server.business.ziqiang.auth as zq_auth
from server.business.wechat.wxa import get_openid


def generate_token_result(
    user: User,
    user_id_field: str,
    expire_time: datetime,
    access: str,
    refresh: str,
) -> dict:
    return dict(
        id=getattr(user, user_id_field),
        username=user.username,
        is_authenticated=user.is_authenticated,
        is_staff=user.is_staff,
        expire_time=expire_time,
        access=access,
        refresh=refresh,
    )


class OpenIdLoginSerializer(DefaultOpenIdLoginSerializer):
    """
    OpenID Token 获取序列化器 (直接用 openid 获取登录 token，用于测试)
    """

    backend = OpenIdBackend(User)  # 自定义验证后端，用于指定不同类型的用户模型

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def generate_token_result(
        self,
        user: User,
        user_id_field: str,
        expire_time: datetime,
        access: str,
        refresh: str,
    ) -> dict:
        return generate_token_result(
            user, user_id_field, expire_time, access, refresh
        )


class WechatLoginSerializer(OpenIdLoginSerializer):
    """
    微信登录序列化器
    """

    code = PasswordField(label="前端获取code")  # 前端传入 code

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields.pop("openid")  # 删除 openid 字段

    def get_open_id(self, attrs: Dict[str, Any]) -> str:
        """
        重写获取 open_id 方法
        """
        return get_openid(attrs["code"])


class UnionIdLoginSerializer(DefaultOpenIdLoginSerializer):
    """
    自强Auth union id 登录序列化器
    """

    backend = UnionIdBackend(User)
    openid = None
    openid_field = "union_id"
    union_id = PasswordField(label="union_id")  # union_id

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def generate_token_result(
        self,
        user: User,
        user_id_field: str,
        expire_time: datetime,
        access: str,
        refresh: str,
    ) -> dict:
        return generate_token_result(
            user, user_id_field, expire_time, access, refresh
        )

    def get_open_id(self, attrs: Dict[str, Any]) -> UUID:
        """
        重写获取 open_id 方法
        """
        return UUID(attrs["union_id"])

    def handle_new_openid(self, union_id: UUID) -> User:
        """
        重写处理新 union id 方法
        """
        try:
            user_data = zq_auth.fetch_user_info(union_id)
            data = {
                "union_id": union_id,
                "username": user_data["name"],
                "phone": user_data["phone"],
                "school_number": user_data["student_id"],
            }
            instance = User.objects.create(
                **data, is_authenticated=True, is_staff=False
            )
            return instance
        except UserNotFoundException:
            raise ApiException(ResponseType.ThirdServiceError, "用户不存在")


class ZqAuthLoginSerializer(UnionIdLoginSerializer):
    """
    自强Auth登录序列化器
    """

    code = PasswordField(label="前端获取code")  # 前端传入 code
    union_id = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_open_id(self, attrs: Dict[str, Any]) -> UUID:
        """
        重写获取 open_id 方法
        """
        return zq_auth.get_union_id(attrs["code"])


class PhoneLoginSerializer(serializers.Serializer):
    """
    手机号+验证码登录序列化器
    """
    
    phone = serializers.CharField(max_length=11, label="手机号")
    verification_code = serializers.CharField(max_length=6, label="验证码")
    
    def validate_phone(self, value):
        """验证手机号格式"""
        import re
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError("手机号格式不正确")
        return value
    
    def validate_verification_code(self, value):
        """验证验证码格式"""
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("验证码格式不正确")
        return value
    
    def validate(self, attrs):
        """验证验证码是否正确"""
        phone = attrs.get('phone')
        verification_code = attrs.get('verification_code')
        
        # 这里应该调用短信验证服务验证验证码
        # 示例：假设验证码存储在缓存中
        # from django.core.cache import cache
        # cached_code = cache.get(f'sms_code_{phone}')
        # if not cached_code or cached_code != verification_code:
        #     raise serializers.ValidationError("验证码错误或已过期")
        
        # 临时跳过验证码验证，实际使用时需要实现短信验证逻辑
        return attrs
    
    def create(self, validated_data):
        """创建或获取用户"""
        phone = validated_data['phone']
        
        # 查找用户
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            # 如果用户不存在，创建新用户
            user = User.objects.create(
                phone=phone,
                username=f"user_{phone}",
                is_authenticated=True,
                is_staff=False
            )
        
        return user


class EmailLoginSerializer(serializers.Serializer):
    """
    武大邮箱登录序列化器
    """
    
    email = serializers.EmailField(label="武大邮箱")
    password = serializers.CharField(max_length=128, label="密码")
    
    def validate_email(self, value):
        """验证武大邮箱格式"""
        # 武大邮箱格式验证：必须是13位+@whu.edu.cn
        if not value.endswith('@whu.edu.cn'):
            raise serializers.ValidationError("邮箱必须以@whu.edu.cn结尾")
        
        # 提取@符号前的部分
        local_part = value.split('@')[0]
        if len(local_part) != 13:
            raise serializers.ValidationError("邮箱前缀必须是13位字符")
        
        return value
    
    def validate(self, attrs):
        """验证邮箱和密码"""
        email = attrs.get('email')
        password = attrs.get('password')
        
        # 查找用户
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("邮箱不存在")
        
        # 验证密码
        if not user.check_password(password):
            raise serializers.ValidationError("密码错误")
        
        # 检查用户是否激活
        if not user.is_authenticated:
            raise serializers.ValidationError("账户未激活")
        
        return attrs
    
    def create(self, validated_data):
        """获取用户"""
        email = validated_data['email']
        user = User.objects.get(email=email)
        return user


class QQBindSerializer(serializers.Serializer):
    """
    QQ绑定序列化器
    """
    
    qq = serializers.CharField(max_length=16, label="QQ号")
    
    def validate_qq(self, value):
        """验证QQ号格式"""
        import re
        if not re.match(r'^\d{5,16}$', value):
            raise serializers.ValidationError("QQ号格式不正确")
        return value
    
    def validate(self, attrs):
        """验证QQ号是否已被绑定"""
        qq = attrs.get('qq')
        
        # 检查QQ号是否已被其他用户绑定
        if User.objects.filter(qq=qq).exists():
            raise serializers.ValidationError("该QQ号已被其他用户绑定")
        
        return attrs


class QQUnbindSerializer(serializers.Serializer):
    """
    QQ解绑序列化器
    """
    
    def validate(self, attrs):
        """验证用户是否已绑定QQ"""
        # 这个验证将在视图中进行，因为需要获取当前用户
        return attrs


class RegisterSerializer(serializers.Serializer):
    """
    简易注册序列化器（用于开发 / MVP）
    """

    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)
    phone = serializers.CharField(max_length=13, required=False, allow_blank=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("用户名已存在")
        return value

    def validate_email(self, value):
        # 如果提供了邮箱，验证格式和唯一性
        if value:
            # 验证武大邮箱格式：必须是13位+@whu.edu.cn
            if not value.endswith('@whu.edu.cn'):
                raise serializers.ValidationError("邮箱必须以@whu.edu.cn结尾")
            
            # 提取@符号前的部分
            local_part = value.split('@')[0]
            if len(local_part) != 13:
                raise serializers.ValidationError("邮箱前缀必须是13位字符")
            
            # 检查邮箱是否已被使用
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("邮箱已被使用")
        
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        # 确保激活并非管理员
        user.is_authenticated = True
        user.is_staff = False
        # 使用 Django 的密码哈希
        user.set_password(password)
        user.save()
        return user


class EmailVerifyCodeSerializer(serializers.Serializer):
    """
    邮箱验证码发送序列化器
    """
    email = serializers.EmailField(label="邮箱")
    
    def validate_email(self, value):
        """验证武大邮箱格式"""
        # 武大邮箱格式验证：必须是13位+@whu.edu.cn
        if not value.endswith('@whu.edu.cn'):
            raise serializers.ValidationError("邮箱必须以@whu.edu.cn结尾")
        
        # 提取@符号前的部分
        local_part = value.split('@')[0]
        if len(local_part) != 13:
            raise serializers.ValidationError("邮箱前缀必须是13位字符")
        
        return value


class EmailVerifySerializer(serializers.Serializer):
    """
    邮箱验证码验证序列化器
    """
    email = serializers.EmailField(label="邮箱")
    code = serializers.CharField(max_length=6, min_length=6, label="验证码")
    
    def validate_email(self, value):
        """验证武大邮箱格式"""
        # 武大邮箱格式验证：必须是13位+@whu.edu.cn
        if not value.endswith('@whu.edu.cn'):
            raise serializers.ValidationError("邮箱必须以@whu.edu.cn结尾")
        
        # 提取@符号前的部分
        local_part = value.split('@')[0]
        if len(local_part) != 13:
            raise serializers.ValidationError("邮箱前缀必须是13位字符")
        
        return value
    
    def validate_code(self, value):
        """验证验证码格式"""
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("验证码格式不正确")
        return value
    
    def validate(self, attrs):
        """验证验证码是否正确"""
        email = attrs.get('email')
        code = attrs.get('code')
        
        # 从缓存中获取验证码
        from django.core.cache import cache
        cache_key = f'email_verify_code_{email}'
        cached_code = cache.get(cache_key)
        
        if not cached_code or cached_code != code:
            raise serializers.ValidationError("验证码错误或已过期")
        
        return attrs
    
    def create(self, validated_data):
        """获取或创建用户"""
        email = validated_data['email']
        
        # 查找用户，如果不存在则创建
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # 自动创建用户
            user = User.objects.create(
                email=email,
                username=f"user_{email.split('@')[0]}",
                is_authenticated=True,
                is_staff=False
            )
        
        # 清除验证码
        from django.core.cache import cache
        cache_key = f'email_verify_code_{email}'
        cache.delete(cache_key)
        
        return user
