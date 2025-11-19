from rest_framework import serializers
from .models import Application
from academies.models import Academy
from users.models import User
from server.utils.choices import GenderType


class ApplicationSerializer(serializers.ModelSerializer):
    """报名表序列化器"""
    
    my_academy_name = serializers.SerializerMethodField()
    academy_choice_names = serializers.SerializerMethodField()
    
    # 前端需要的字段（从 User 模型获取）
    name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    degree = serializers.SerializerMethodField()
    studentNo = serializers.SerializerMethodField()
    majorCategory = serializers.SerializerMethodField()
    college = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()
    
    def get_name(self, obj):
        """获取用户名"""
        try:
            return obj.user.username if obj and hasattr(obj, 'user') and obj.user else ''
        except Exception:
            return ''
    
    def get_studentNo(self, obj):
        """获取学号"""
        try:
            return obj.user.school_number if obj and hasattr(obj, 'user') and obj.user else ''
        except Exception:
            return ''
    
    def get_bio(self, obj):
        """获取个人简介"""
        try:
            return obj.user.interest if obj and hasattr(obj, 'user') and obj.user else ''
        except Exception:
            return ''
    
    def get_my_academy_name(self, obj):
        """获取我的院系名称"""
        try:
            if not obj or not hasattr(obj, 'my_academy') or not obj.my_academy:
                return None
            return obj.my_academy.name
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"获取院系名称失败: {e}")
            return None
    
    def get_avatar(self, obj):
        """获取头像 URL"""
        try:
            if not obj or not hasattr(obj, 'user') or not obj.user:
                return ''
            if not hasattr(obj.user, 'avatar') or not obj.user.avatar:
                return ''
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.user.avatar.url)
            return obj.user.avatar.url if hasattr(obj.user.avatar, 'url') else ''
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"获取头像URL失败: {e}")
            return ''
    
    def get_gender(self, obj):
        """获取性别（转换为字符串）"""
        try:
            if not obj or not hasattr(obj, 'user') or not obj.user:
                return ''
            from server.utils.choices import GenderType
            gender_map = {
                GenderType.MALE: '男',
                GenderType.FEMALE: '女',
                GenderType.UNKNOWN: ''
            }
            return gender_map.get(obj.user.gender, '')
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"获取性别失败: {e}")
            return ''
    
    def get_degree(self, obj):
        """获取学历（从年级推断）"""
        try:
            if not obj or not hasattr(obj, 'user') or not obj.user:
                return ''
            # 根据年级推断学历：1-4年级为本科，5-6年级为研究生
            grade = getattr(obj.user, 'grade', 0) or 0
            if grade <= 4:
                return '本科'
            elif grade <= 6:
                return '研究生'
            return ''
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"获取学历失败: {e}")
            return ''
    
    def get_majorCategory(self, obj):
        """获取专业大类"""
        # 这里需要根据实际业务逻辑返回专业大类
        # 暂时返回空字符串
        return ''
    
    def get_college(self, obj):
        """获取院系名称"""
        return self.get_my_academy_name(obj) or ''
    
    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ('user',)
    
    def get_academy_choice_names(self, obj):
        """获取选择的院系名称列表"""
        try:
            if not obj or not hasattr(obj, 'academy_choice'):
                return []
            return [academy.name for academy in obj.academy_choice.all()]
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"获取院系选择列表失败: {e}")
            return []
    
    def validate_phone(self, value):
        """验证手机号格式"""
        import re
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError("手机号格式不正确")
        return value
    
    def validate_qq(self, value):
        """验证QQ号格式"""
        import re
        if not re.match(r'^\d{5,16}$', value):
            raise serializers.ValidationError("QQ号格式不正确")
        return value
    
    def validate(self, attrs):
        """验证院系选择"""
        # 检查我的院系是否在交换院系中
        my_academy = attrs.get('my_academy')
        academy_choice = self.initial_data.get('academy_choice', [])
        
        if my_academy and str(my_academy.id) in [str(a) for a in academy_choice]:
            raise serializers.ValidationError("不能选择自己的院系进行交换")
        
        return attrs
    
    def create(self, validated_data):
        """创建报名表"""
        # 自动关联当前用户
        validated_data['user'] = self.context['request'].user
        
        # 处理多对多字段
        academy_choice = validated_data.pop('academy_choice', [])
        application = Application.objects.create(**validated_data)
        application.academy_choice.set(academy_choice)
        
        return application


class SignupSerializer(serializers.Serializer):
    """
    前端报名数据序列化器（适配前端数据格式）
    """
    name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    gender = serializers.CharField(max_length=10, required=False, allow_blank=True)
    degree = serializers.CharField(max_length=20, required=False, allow_blank=True)
    studentNo = serializers.CharField(max_length=20, required=False, allow_blank=True)
    majorCategory = serializers.CharField(max_length=50, required=False, allow_blank=True)
    college = serializers.CharField(max_length=100, required=False, allow_blank=True)
    qq = serializers.CharField(max_length=16, required=False, allow_blank=True)
    bio = serializers.CharField(max_length=500, required=False, allow_blank=True)
    avatar = serializers.CharField(max_length=500, required=False, allow_blank=True)
    signupType = serializers.CharField(max_length=20, required=False, allow_blank=True)
    
    def validate(self, attrs):
        """验证院系是否存在"""
        college_name = attrs.get('college')
        if college_name:
            try:
                academy = Academy.objects.get(name=college_name)
                attrs['_college_academy'] = academy  # 存储 Academy 对象供 create 使用
            except Academy.DoesNotExist:
                raise serializers.ValidationError(f"院系 '{college_name}' 不存在")
        return attrs
    
    def validate_qq(self, value):
        """验证QQ号格式"""
        if value:
            import re
            if not re.match(r'^\d{5,16}$', value):
                raise serializers.ValidationError("QQ号格式不正确")
        return value
    
    def validate_gender(self, value):
        """转换性别格式"""
        if not value:
            return '无'
        gender_map = {
            '男': '男',
            '女': '女',
            'male': '男',
            'female': '女',
            'MALE': '男',
            'FEMALE': '女',
        }
        return gender_map.get(value, '无')
    
    def validate_degree(self, value):
        """转换学历格式"""
        if not value:
            return ''
        degree_map = {
            '本科': '本科',
            '研究生': '研究生',
            'undergraduate': '本科',
            'postgraduate': '研究生',
            'graduate': '研究生',  # 兼容可能的 'graduate' 值
            'UNDERGRADUATE': '本科',
            'POSTGRADUATE': '研究生',
        }
        return degree_map.get(value, '')
    
    def create(self, validated_data):
        """创建报名表并更新用户信息"""
        request = self.context['request']
        user = request.user
        
        # 更新用户信息
        if validated_data.get('name'):
            user.username = validated_data['name']
        if validated_data.get('studentNo'):
            user.school_number = validated_data['studentNo']
        if validated_data.get('bio'):
            user.interest = validated_data['bio']
        if validated_data.get('qq'):
            user.qq = validated_data['qq']
        if validated_data.get('avatar'):
            user.avatar = validated_data['avatar']
        
        # 转换性别
        gender_str = validated_data.get('gender', '')
        if gender_str == '男':
            user.gender = GenderType.MALE
        elif gender_str == '女':
            user.gender = GenderType.FEMALE
        else:
            user.gender = GenderType.UNKNOWN
        
        # 根据学历设置年级（简化处理）
        degree = validated_data.get('degree', '')
        if degree == '本科':
            user.grade = 1  # 默认一年级
        elif degree == '研究生':
            user.grade = 5  # 默认研一
        
        # 设置院系
        college_academy = validated_data.pop('_college_academy', None)
        college_name = validated_data.get('college', '')
        
        if college_academy:
            user.academy = college_academy
        
        user.save()
        
        # 创建报名表
        # 获取用户的手机号，如果没有则使用空字符串
        phone = user.phone if hasattr(user, 'phone') and user.phone else ''
        
        application_data = {
            'user': user,
            'my_academy': college_academy,
            'my_gender': validated_data.get('gender', '无'),
            'gender_choice': '无',  # 前端没有这个字段，默认值
            'phone': phone,  # 使用用户的手机号
            'qq': validated_data.get('qq', ''),
        }
        
        application = Application.objects.create(**application_data)
        
        # 设置愿意交换的专业（前端没有这个字段，暂时为空）
        # academy_choice = validated_data.get('academy_choice', [])
        # application.academy_choice.set(academy_choice)
        
        return application
