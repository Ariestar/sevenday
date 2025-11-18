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
    OpenIdLoginView,
    PhoneLoginView,
    QQBindView,
    QQUnbindView,
    UnionIdLoginView,
    WechatLoginView,
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
