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
        try:
            if not obj or not hasattr(obj, 'user') or not obj.user:
                return ''
            # 尝试从 User 模型获取 major_category 字段
            # 如果字段不存在，返回空字符串（兼容旧数据）
            user = obj.user
            if hasattr(user, 'major_category'):
                try:
                    return getattr(user, 'major_category', '') or ''
                except AttributeError:
                    # 字段不存在（迁移未运行）
                    return ''
            # 如果 User 模型没有这个字段，返回空
            return ''
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"获取专业大类失败: {e}", exc_info=True)
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
    avatar = serializers.CharField(max_length=500, required=False, allow_blank=True, allow_null=True)
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
    
    def _extract_student_no_from_email(self, email):
        """从邮箱中提取学号（武大邮箱格式：学号@whu.edu.cn）"""
        if not email:
            return None
        
        # 提取 @ 之前的部分作为学号
        if '@' in email:
            student_no = email.split('@')[0]
            # 验证是否为有效的学号格式（通常是数字）
            if student_no and student_no.isdigit():
                return student_no
        
        return None
    
    def create(self, validated_data):
        """创建报名表并更新用户信息"""
        request = self.context['request']
        user = request.user
        
        # 更新用户信息
        if validated_data.get('name'):
            user.username = validated_data['name']
        
        # 处理学号：优先使用提交的学号，如果没有则从邮箱提取
        if 'studentNo' in validated_data:
            student_no = validated_data.get('studentNo', '').strip()
            if student_no:
                user.school_number = student_no
            elif not user.school_number or user.school_number.strip() == '':
                # 如果学号为空，尝试从邮箱提取
                email = user.email
                if email:
                    extracted_student_no = self._extract_student_no_from_email(email)
                    if extracted_student_no:
                        user.school_number = extracted_student_no
        
        if 'bio' in validated_data:
            user.interest = validated_data.get('bio', '').strip()
        if 'qq' in validated_data:
            user.qq = validated_data.get('qq', '').strip()
        
        # 处理头像：如果传递的是完整URL，需要提取相对路径
        if 'avatar' in validated_data:
            avatar_value = validated_data.get('avatar', '').strip()
            if avatar_value:
                # 如果传递的是完整URL，提取相对路径
                if avatar_value.startswith('http://') or avatar_value.startswith('https://'):
                    # 提取 /media/ 之后的部分
                    if '/media/' in avatar_value:
                        # 解码URL，然后提取相对路径
                        import urllib.parse
                        # 多次解码直到得到原始路径
                        decoded = avatar_value
                        max_decode_attempts = 10  # 限制解码次数，避免无限循环
                        decode_count = 0
                        while '%' in decoded and decode_count < max_decode_attempts:
                            try:
                                new_decoded = urllib.parse.unquote(decoded)
                                if new_decoded == decoded:  # 如果解码后没有变化，停止
                                    break
                                decoded = new_decoded
                                decode_count += 1
                            except:
                                break
                        # 提取 media/ 之后的部分
                        if '/media/' in decoded:
                            relative_path = decoded.split('/media/')[-1]
                            # 检查路径长度，如果超过500字符，使用默认头像
                            if len(relative_path) > 500:
                                user.avatar = 'avatar/default.jpg'
                            else:
                                user.avatar = relative_path
                        else:
                            # 如果无法提取，使用默认头像
                            user.avatar = 'avatar/default.jpg'
                    else:
                        # 如果URL格式不对，使用默认头像
                        user.avatar = 'avatar/default.jpg'
                else:
                    # 如果已经是相对路径，检查长度
                    if len(avatar_value) > 500:
                        # 如果相对路径太长，使用默认头像
                        user.avatar = 'avatar/default.jpg'
                    else:
                        user.avatar = avatar_value
        # 保存专业大类
        if validated_data.get('majorCategory'):
            try:
                if hasattr(user, 'major_category'):
                    user.major_category = validated_data['majorCategory']
                else:
                    # 如果字段不存在（迁移未运行），记录警告但不阻止保存
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"User 模型没有 major_category 字段，请运行迁移: python manage.py migrate users")
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"保存专业大类失败: {e}")
        
        # 转换性别：兼容前端传递的英文格式和中文格式
        if 'gender' in validated_data:
            gender_str = validated_data.get('gender', '').strip()
            if gender_str == '男' or gender_str == 'male' or gender_str == 'MALE':
                user.gender = GenderType.MALE
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"用户 {user.id} 创建时设置性别: {gender_str} -> MALE")
            elif gender_str == '女' or gender_str == 'female' or gender_str == 'FEMALE':
                user.gender = GenderType.FEMALE
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"用户 {user.id} 创建时设置性别: {gender_str} -> FEMALE")
            else:
                user.gender = GenderType.UNKNOWN
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"用户 {user.id} 创建时性别值无法识别: {gender_str}，设置为UNKNOWN")
        
        # 根据学历设置年级：兼容前端传递的英文格式和中文格式
        if 'degree' in validated_data:
            degree = validated_data.get('degree', '').strip()
            if degree == '本科' or degree == 'undergraduate' or degree == 'UNDERGRADUATE':
                user.grade = 1  # 默认一年级
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"用户 {user.id} 创建时设置学历: {degree} -> grade=1 (本科)")
            elif degree == '研究生' or degree == 'postgraduate' or degree == 'graduate' or degree == 'POSTGRADUATE' or degree == 'GRADUATE':
                user.grade = 5  # 默认研一
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"用户 {user.id} 创建时设置学历: {degree} -> grade=5 (研究生)")
            else:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"用户 {user.id} 创建时学历值无法识别: {degree}，保持原grade值: {user.grade}")
        # 如果学历为空或无法识别，保持原值（不强制设置）
        
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
    
    def update(self, instance, validated_data):
        """更新报名表并更新用户信息"""
        request = self.context['request']
        user = request.user
        
        # 更新用户信息
        if 'name' in validated_data:
            user.username = validated_data['name']
        
        # 处理学号：优先使用提交的学号，如果没有则从邮箱提取
        if 'studentNo' in validated_data:
            student_no = validated_data.get('studentNo', '').strip()
            if student_no:
                user.school_number = student_no
            elif not user.school_number or user.school_number.strip() == '':
                # 如果学号为空，尝试从邮箱提取
                email = user.email
                if email:
                    extracted_student_no = self._extract_student_no_from_email(email)
                    if extracted_student_no:
                        user.school_number = extracted_student_no
        
        if 'bio' in validated_data:
            user.interest = validated_data.get('bio', '').strip()
        if 'qq' in validated_data:
            user.qq = validated_data.get('qq', '').strip()
        
        # 处理头像：如果传递的是完整URL，需要提取相对路径
        if 'avatar' in validated_data:
            avatar_value = validated_data.get('avatar')
            # 处理None、空字符串等情况
            if avatar_value is None:
                # 如果传递None，不更新头像
                pass
            elif isinstance(avatar_value, str):
                avatar_value = avatar_value.strip()
                if avatar_value:
                    # 如果传递的是完整URL，提取相对路径
                    if avatar_value.startswith('http://') or avatar_value.startswith('https://'):
                        # 提取 /media/ 之后的部分
                        if '/media/' in avatar_value:
                            # 解码URL，然后提取相对路径
                            import urllib.parse
                            # 多次解码直到得到原始路径
                            decoded = avatar_value
                            max_decode_attempts = 10  # 限制解码次数，避免无限循环
                            decode_count = 0
                            while '%' in decoded and decode_count < max_decode_attempts:
                                try:
                                    new_decoded = urllib.parse.unquote(decoded)
                                    if new_decoded == decoded:  # 如果解码后没有变化，停止
                                        break
                                    decoded = new_decoded
                                    decode_count += 1
                                except:
                                    break
                            # 提取 media/ 之后的部分
                            if '/media/' in decoded:
                                relative_path = decoded.split('/media/')[-1]
                                # 检查路径长度，如果超过500字符，使用默认头像
                                if len(relative_path) > 500:
                                    user.avatar = 'avatar/default.jpg'
                                else:
                                    user.avatar = relative_path
                            else:
                                # 如果无法提取，保持原值（不更新头像）
                                pass
                        else:
                            # 如果URL格式不对，保持原值（不更新头像）
                            pass
                    else:
                        # 如果已经是相对路径，检查长度
                        if len(avatar_value) > 500:
                            # 如果相对路径太长，使用默认头像
                            user.avatar = 'avatar/default.jpg'
                        else:
                            user.avatar = avatar_value
        
        # 保存专业大类
        if 'majorCategory' in validated_data:
            try:
                if hasattr(user, 'major_category'):
                    user.major_category = validated_data['majorCategory']
                else:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"User 模型没有 major_category 字段，请运行迁移")
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"保存专业大类失败: {e}")
        
        # 转换性别：兼容前端传递的英文格式和中文格式
        if 'gender' in validated_data:
            gender_str = validated_data.get('gender', '').strip()
            if gender_str == '男' or gender_str == 'male' or gender_str == 'MALE':
                user.gender = GenderType.MALE
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"用户 {user.id} 更新性别: {gender_str} -> MALE")
            elif gender_str == '女' or gender_str == 'female' or gender_str == 'FEMALE':
                user.gender = GenderType.FEMALE
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"用户 {user.id} 更新性别: {gender_str} -> FEMALE")
            else:
                user.gender = GenderType.UNKNOWN
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"用户 {user.id} 性别值无法识别: {gender_str}，设置为UNKNOWN")
        
        # 根据学历设置年级：兼容前端传递的英文格式和中文格式
        if 'degree' in validated_data:
            degree = validated_data.get('degree', '').strip()
            if degree == '本科' or degree == 'undergraduate' or degree == 'UNDERGRADUATE':
                user.grade = 1
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"用户 {user.id} 更新学历: {degree} -> grade=1 (本科)")
            elif degree == '研究生' or degree == 'postgraduate' or degree == 'graduate' or degree == 'POSTGRADUATE' or degree == 'GRADUATE':
                user.grade = 5
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"用户 {user.id} 更新学历: {degree} -> grade=5 (研究生)")
            else:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"用户 {user.id} 学历值无法识别: {degree}，保持原grade值: {user.grade}")
        # 如果学历为空或无法识别，保持原值（不强制设置）
        
        # 设置院系
        college_academy = validated_data.pop('_college_academy', None)
        college_name = validated_data.get('college', '')
        
        if college_academy:
            user.academy = college_academy
        
        user.save()
        
        # 更新报名表
        if college_academy:
            instance.my_academy = college_academy
        
        if 'gender' in validated_data:
            instance.my_gender = validated_data.get('gender', '无')
        
        if 'qq' in validated_data:
            instance.qq = validated_data.get('qq', '')
        
        instance.save()
        
        return instance


class MatchExpectationSerializer(serializers.Serializer):
    """匹配期望序列化器"""
    gender = serializers.CharField(max_length=10, required=False, allow_blank=True, help_text='期望性别：男/女/不限')
    degree = serializers.CharField(max_length=20, required=False, allow_blank=True, help_text='期望学历：本科/研究生')
    majorCategory = serializers.CharField(max_length=50, required=False, allow_blank=True, help_text='期望大类')
    college = serializers.CharField(max_length=100, required=False, allow_blank=True, help_text='期望学院名称')
    
    def validate_college(self, value):
        """验证学院是否存在，返回学院名称（不转换为对象）"""
        if value:
            try:
                academy = Academy.objects.get(name=value)
                # 返回学院名称，让视图层处理转换
                return value
            except Academy.DoesNotExist:
                raise serializers.ValidationError(f"院系 '{value}' 不存在")
        return value