from rest_framework import serializers
from .models import Application
from academies.models import Academy


class ApplicationSerializer(serializers.ModelSerializer):
    """报名表序列化器"""
    
    my_academy_name = serializers.CharField(source='my_academy.name', read_only=True)
    academy_choice_names = serializers.SerializerMethodField()
    
    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ('user',)
    
    def get_academy_choice_names(self, obj):
        """获取选择的院系名称列表"""
        return [academy.name for academy in obj.academy_choice.all()]
    
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
