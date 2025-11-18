from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView
from users.models import User
from zq_django_util.exceptions import ApiException
from zq_django_util.response import ResponseType

from .serializers import (
    EmailLoginSerializer,
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

