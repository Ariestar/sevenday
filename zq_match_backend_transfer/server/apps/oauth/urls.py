from django.urls import path
from django.conf import settings
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from django.urls import path
from django.conf import settings
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    EmailLoginView,
    EmailVerifyCodeView,
    EmailVerifyView,
    OpenIdLoginView,
    PhoneLoginView,
    QQBindView,
    QQUnbindView,
    UnionIdLoginView,
    UpdateUserInfoView,
    UserInfoView,
    WechatLoginView,
    WxLoginView,
    ZqAuthLoginView,
    RegisterView,
)

router = routers.SimpleRouter()

urlpatterns = [
    path("login/", EmailLoginView.as_view(), name="email_login"),  # 武大邮箱登录（统一登录入口）
    path("register/", RegisterView.as_view(), name="register"),  # 简易注册（开发用）
    path("bind/qq/", QQBindView.as_view(), name="qq_bind"),  # QQ绑定
    path("unbind/qq/", QQUnbindView.as_view(), name="qq_unbind"),  # QQ解绑
    path(
        "refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),  # 刷新token
    # 邮箱验证码登录接口（前端使用）
    path("sendCode/", EmailVerifyCodeView.as_view(), name="email_send_code"),  # 发送邮箱验证码
    path("sendCode", EmailVerifyCodeView.as_view(), name="email_send_code_no_slash"),  # 发送邮箱验证码（无斜杠版本）
    path("verify/", EmailVerifyView.as_view(), name="email_verify"),  # 验证邮箱验证码并登录
    path("verify", EmailVerifyView.as_view(), name="email_verify_no_slash"),  # 验证邮箱验证码并登录（无斜杠版本）
    path("userInfo/", UserInfoView.as_view(), name="user_info"),  # 获取当前用户信息
    path("userInfo", UserInfoView.as_view(), name="user_info_no_slash"),  # 获取当前用户信息（无斜杠版本）
    path("updateUserInfo/", UpdateUserInfoView.as_view(), name="update_user_info"),  # 更新用户信息
    path("updateUserInfo", UpdateUserInfoView.as_view(), name="update_user_info_no_slash"),  # 更新用户信息（无斜杠版本）
    path("wxLogin/", WxLoginView.as_view(), name="wx_login"),  # 微信登录（前端使用）
    path("wxLogin", WxLoginView.as_view(), name="wx_login_no_slash"),  # 微信登录（无斜杠版本）
    # 以下登录方式已禁用，仅保留武大邮箱登录+QQ绑定功能
    # path("qq/", QQLoginView.as_view(), name="qq_login"),  # QQ登录（已禁用）
    # path("wechat/", WechatLoginView.as_view(), name="wechat_login"),  # 微信登录（已禁用）
    # path("phone/", PhoneLoginView.as_view(), name="phone_login"),  # 手机号登录（已禁用）
    # path(
    #     "zq/",
    #     ZqAuthLoginView.as_view(),
    #     name="zq_auth_login",
    # ),  # ZqAuth登录（已禁用）
    # path(
    #     "wechat/openid/", OpenIdLoginView.as_view(), name="openid_pair"
    # ),  # openid登录（已禁用）
    # path(
    #     "zq/unionid/",
    #     UnionIdLoginView.as_view(),
    #     name="zq_auth_union_id",
    # ),  # ZqAuth登录（已禁用）
]

urlpatterns += router.urls
