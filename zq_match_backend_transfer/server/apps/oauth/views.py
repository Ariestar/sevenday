from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView
from users.models import User
from users.serializers import UserSerializer
from zq_django_util.exceptions import ApiException
from zq_django_util.response import ResponseType

from .serializers import (
    EmailLoginSerializer,
    EmailVerifyCodeSerializer,
    EmailVerifySerializer,
    OpenIdLoginSerializer,
    PhoneLoginSerializer,
    QQBindSerializer,
    QQUnbindSerializer,
    UnionIdLoginSerializer,
    WechatLoginSerializer,
    ZqAuthLoginSerializer,
)
from .serializers import RegisterSerializer
from zq_django_util.response import ResponseType
from zq_django_util.exceptions import ApiException
from django.shortcuts import render
from django.views import View
from rest_framework_simplejwt.tokens import RefreshToken


class OpenIdLoginView(TokenObtainPairView):
    """
    open id 登录视图（仅供测试微信登录使用）
    """

    queryset = User.objects.all()
    serializer_class = OpenIdLoginSerializer

    def post(self, request, *args, **kwargs):
        """
        增加 post 方法, 支持 open id 登录
        """
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            raise ApiException(
                ResponseType.ThirdLoginFailed,
                msg="微信登录失败",
                detail="生成token时simple jwt发生TokenError",
                record=True,
            )

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class WechatLoginView(OpenIdLoginView):
    """
    微信登录视图
    """

    queryset = User.objects.all()
    serializer_class = WechatLoginSerializer


class UnionIdLoginView(TokenObtainPairView):
    """
    zq auth union id 登录视图
    """

    queryset = User.objects.all()
    serializer_class = UnionIdLoginSerializer

    def post(self, request, *args, **kwargs):
        """
        增加 post 方法, 支持 sso 登录
        """
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            raise ApiException(
                ResponseType.ThirdLoginFailed,
                msg="自强账号登录失败",
                detail="生成token时simple jwt发生TokenError",
                record=True,
            )

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class ZqAuthLoginView(UnionIdLoginView):
    """
    zq auth 登录视图
    """


class PhoneLoginView(TokenObtainPairView):
    """
    手机号+验证码登录视图
    """
    
    queryset = User.objects.all()
    serializer_class = PhoneLoginSerializer
    
    def post(self, request, *args, **kwargs):
        """
        手机号+验证码登录
        """
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            raise ApiException(
                ResponseType.ThirdLoginFailed,
                msg="手机号登录失败",
                detail=str(e),
                record=True,
            )
        
        # 获取用户
        user = serializer.create(serializer.validated_data)
        
        # 生成JWT token
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        
        # 返回token信息
        return Response({
            'id': user.id,
            'username': user.username,
            'is_authenticated': user.is_authenticated,
            'is_staff': user.is_staff,
            'access': str(access),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)


class EmailLoginView(TokenObtainPairView):
    """
    武大邮箱登录视图
    """
    
    queryset = User.objects.all()
    serializer_class = EmailLoginSerializer
    
    def post(self, request, *args, **kwargs):
        """
        武大邮箱登录
        """
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            raise ApiException(
                ResponseType.ThirdLoginFailed,
                msg="武大邮箱登录失败",
                detail=str(e),
                record=True,
            )
        
        # 获取用户
        user = serializer.create(serializer.validated_data)
        
        # 生成JWT token
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        
        # 返回token信息
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_authenticated': user.is_authenticated,
            'is_staff': user.is_staff,
            'access': str(access),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)


class QQBindView(APIView):
    """
    QQ绑定视图
    """
    
    def post(self, request):
        """
        绑定QQ号
        """
        serializer = QQBindSerializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="QQ绑定失败",
                detail=str(e),
                record=True,
            )
        
        # 获取当前用户（需要JWT认证）
        user = request.user
        if not user.is_authenticated:
            raise ApiException(
                ResponseType.Unauthorized,
                msg="请先登录",
                record=True,
            )
        
        # 检查用户是否已绑定QQ
        if user.qq:
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="您已绑定QQ号，请先解绑",
                record=True,
            )
        
        # 绑定QQ号
        qq = serializer.validated_data['qq']
        user.qq = qq
        user.save()
        
        return Response({
            'message': 'QQ绑定成功',
            'qq': qq,
        }, status=status.HTTP_200_OK)


class QQUnbindView(APIView):
    """
    QQ解绑视图
    """
    
    def post(self, request):
        """
        解绑QQ号
        """
        # 获取当前用户（需要JWT认证）
        user = request.user
        if not user.is_authenticated:
            raise ApiException(
                ResponseType.Unauthorized,
                msg="请先登录",
                record=True,
            )
        
        # 检查用户是否已绑定QQ
        if not user.qq:
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="您尚未绑定QQ号",
                record=True,
            )
        
        # 解绑QQ号
        old_qq = user.qq
        user.qq = ""
        user.save()
        
        return Response({
            'message': 'QQ解绑成功',
            'unbound_qq': old_qq,
        }, status=status.HTTP_200_OK)



class RegisterView(APIView):
    """
    简易注册视图（用于本地开发 / MVP）
    """

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="注册失败",
                detail=str(e),
                record=True,
            )

        user = serializer.create(serializer.validated_data)

        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_authenticated': user.is_authenticated,
        }, status=status.HTTP_201_CREATED)


class EmailVerifyCodeView(APIView):
    """
    发送邮箱验证码视图
    """
    
    def post(self, request):
        """
        发送邮箱验证码
        """
        serializer = EmailVerifyCodeSerializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="邮箱格式不正确",
                detail=str(e),
                record=True,
            )
        
        email = serializer.validated_data['email']
        
        # 生成6位随机验证码
        import random
        verify_code = str(random.randint(100000, 999999))
        
        # 将验证码存储到缓存中，有效期5分钟
        from django.core.cache import cache
        cache_key = f'email_verify_code_{email}'
        cache.set(cache_key, verify_code, 300)  # 5分钟过期
        
        # 发送邮件
        import logging
        logger = logging.getLogger(__name__)
        
        # 检查是否配置了邮件服务器
        email_configured = bool(getattr(settings, 'EMAIL_HOST_USER', None))
        
        if email_configured:
            # 配置了邮件服务器，发送真实邮件
            try:
                # 渲染邮件模板
                html_message = render_to_string(
                    'email/verify_code.html',
                    {
                        'email': email,
                        'verify_code': verify_code
                    }
                )
                text_message = render_to_string(
                    'email/verify_code.txt',
                    {
                        'email': email,
                        'verify_code': verify_code
                    }
                )
                
                # 发送邮件前记录详细信息
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
                logger.info(f"准备发送邮件 - 发件人: {from_email}, 收件人: {email}, SMTP服务器: {getattr(settings, 'EMAIL_HOST', 'N/A')}")
                
                if getattr(settings, 'DEBUG', False):
                    print(f"\n{'='*60}")
                    print(f"📤 准备发送邮件")
                    print(f"   发件人: {from_email}")
                    print(f"   收件人: {email}")
                    print(f"   SMTP服务器: {getattr(settings, 'EMAIL_HOST', 'N/A')}:{getattr(settings, 'EMAIL_PORT', 'N/A')}")
                    print(f"   验证码: {verify_code}")
                    print(f"{'='*60}\n")
                
                # 发送邮件
                if getattr(settings, 'DEBUG', False):
                    print(f"⏳ 正在调用 send_mail()...")
                
                try:
                    import time
                    start_time = time.time()
                    
                    result = send_mail(
                        subject='专交遇见你 - 邮箱验证码',
                        message=text_message,
                        from_email=from_email,
                        recipient_list=[email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    
                    elapsed_time = time.time() - start_time
                    
                    # send_mail返回成功发送的邮件数量（通常是1）
                    logger.info(f"邮件发送完成 - 返回值: {result}, 耗时: {elapsed_time:.2f}秒, 收件人: {email}")
                    
                    if getattr(settings, 'DEBUG', False):
                        print(f"⏱️  send_mail() 执行完成，耗时: {elapsed_time:.2f}秒")
                        print(f"📊 send_mail() 返回值: {result}")
                    
                    if result == 0:
                        # 发送失败但没有抛出异常的情况
                        error_msg = "send_mail返回0，表示邮件未成功发送"
                        logger.error(error_msg)
                        if getattr(settings, 'DEBUG', False):
                            print(f"❌ {error_msg}")
                        raise Exception(error_msg)
                    
                    logger.info(f"验证码邮件已成功发送到: {email}")
                    
                    # 开发环境：同时在控制台输出验证码（便于调试）
                    if getattr(settings, 'DEBUG', False):
                        print(f"\n{'='*60}")
                        print(f"✅ 验证码邮件已发送到: {email}")
                        print(f"📧 验证码: {verify_code}")
                        print(f"💡 提示: 如果未收到邮件，请检查垃圾箱")
                        print(f"{'='*60}\n")
                        
                except Exception as send_error:
                    # 捕获send_mail内部的异常
                    error_msg = str(send_error)
                    error_type = type(send_error).__name__
                    logger.error(f"send_mail执行失败 - 类型: {error_type}, 错误: {error_msg}", exc_info=True)
                    
                    if getattr(settings, 'DEBUG', False):
                        print(f"\n{'='*60}")
                        print(f"❌ send_mail() 执行失败")
                        print(f"   错误类型: {error_type}")
                        print(f"   错误信息: {error_msg}")
                        print(f"   验证码: {verify_code} (已保存到缓存)")
                        print(f"{'='*60}\n")
                    
                    raise Exception(f"邮件发送失败 [{error_type}]: {error_msg}")
                
                # 返回数据，让自定义渲染器自动包装
                # 开发环境返回验证码，生产环境应移除
                data = {}
                if getattr(settings, 'DEBUG', False):
                    data['verifyCode'] = verify_code
                
                return Response(data, status=status.HTTP_200_OK)
                
            except Exception as e:
                logger.error(f"发送验证码邮件失败: {e}")
                
                # 开发环境：邮件发送失败时在控制台输出验证码
                if getattr(settings, 'DEBUG', False):
                    print(f"\n{'='*60}")
                    print(f"⚠️  邮件发送失败，验证码 [{email}]: {verify_code}")
                    print(f"错误: {e}")
                    print(f"{'='*60}\n")
                    
                    # 返回数据，让自定义渲染器自动包装（开发环境）
                    return Response({
                        'verifyCode': verify_code
                    }, status=status.HTTP_200_OK)
                else:
                    # 生产环境：邮件发送失败时抛出异常
                    raise ApiException(
                        ResponseType.ServerError,
                        msg="验证码发送失败，请稍后重试",
                        detail=str(e),
                        record=True,
                    )
        else:
            # 未配置邮件服务器，使用控制台输出（开发环境）
            logger.info(f"邮箱验证码 [{email}]: {verify_code}")
            print(f"\n{'='*60}")
            print(f"📧 邮箱验证码 [{email}]: {verify_code}")
            print(f"💡 提示: 未配置邮件服务器，验证码仅在控制台输出")
            print(f"{'='*60}\n")
            
            # 返回数据，让自定义渲染器自动包装（开发环境）
            return Response({
                'verifyCode': verify_code
            }, status=status.HTTP_200_OK)


class EmailVerifyView(APIView):
    """
    邮箱验证码验证登录视图
    """
    
    def post(self, request):
        """
        验证邮箱验证码并登录
        """
        # 调试日志：打印接收到的数据
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"收到验证请求: {request.data}")
        print(f"\n收到验证请求:")
        print(f"  email: {request.data.get('email')}")
        print(f"  code: {request.data.get('code')}")
        print(f"  code type: {type(request.data.get('code'))}")
        print(f"  code length: {len(str(request.data.get('code', ''))) if request.data.get('code') else 0}")
        
        serializer = EmailVerifySerializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            logger.error(f"验证失败: {e}")
            print(f"验证失败: {e}")
            raise ApiException(
                ResponseType.ThirdLoginFailed,
                msg="邮箱验证失败",
                detail=str(e),
                record=True,
            )
        
        # 获取或创建用户
        user = serializer.create(serializer.validated_data)
        
        # 生成JWT token
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        
        # 返回数据，让自定义渲染器自动包装
        return Response({
            'token': str(access),
            'refresh': str(refresh),
            'userInfo': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_authenticated': user.is_authenticated,
                'is_staff': user.is_staff,
            }
        }, status=status.HTTP_200_OK)


class UserInfoView(APIView):
    """
    获取当前用户信息视图
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        获取当前用户信息
        """
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


class UpdateUserInfoView(APIView):
    """
    更新用户信息视图
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        更新用户信息
        """
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="更新用户信息失败",
                detail=str(e),
                record=True,
            )
        
        serializer.save()
        return Response(serializer.data)


class WxLoginView(APIView):
    """
    微信登录视图（前端使用）
    """
    
    def post(self, request):
        """
        微信登录
        """
        code = request.data.get('code')
        
        if not code:
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="请提供code参数",
            )
        
        try:
            # 使用微信小程序登录获取openid
            from server.business.wechat.wxa import get_openid
            openid = get_openid(code)
            
            # 查找或创建用户
            user, created = User.objects.get_or_create(
                openid=openid,
                defaults={
                    'username': f'wx_user_{openid[:8]}',
                    'is_authenticated': True,
                }
            )
            
            # 如果用户已存在但未激活，激活用户
            if not created and not user.is_authenticated:
                user.is_authenticated = True
                user.save()
            
            # 生成JWT token
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            
            # 返回token和用户信息
            return Response({
                'code': '00000',
                'msg': '登录成功',
                'data': {
                    'token': str(access),
                    'refresh': str(refresh),
                    'userInfo': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'is_authenticated': user.is_authenticated,
                        'is_staff': user.is_staff,
                    }
                }
            }, status=status.HTTP_200_OK)
            
        except ApiException:
            raise
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"微信登录失败: {e}", exc_info=True)
            raise ApiException(
                ResponseType.ThirdLoginFailed,
                msg="微信登录失败，请稍后重试",
                detail=str(e),
                record=True,
            )

