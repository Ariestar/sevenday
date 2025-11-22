from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

# from apps.users.views import UsersInfoView as UsersInfoView
urlpatterns = [
    path("admin/", admin.site.urls),  # admin 后台管理
    path(
        "favicon.ico",
        RedirectView.as_view(
            url="https://zq-public-oss.oss-cn-hangzhou.aliyuncs.com/zq-auth/backend/static/static/favorite.ico"
        ),
    ),

    # 根路径重定向到 admin 后台，避免在开发时访问 / 时出现 404
    path("", RedirectView.as_view(url="/admin/")),
    path("oauth/", include("oauth.urls")),  # 登录
    path("auth/", include("oauth.urls")),  # 邮箱验证码登录（前端使用）
    path("academies/", include("academies.urls")),  # 院系
    path("applications/", include("applications.urls")),  # 报名表
    path("signup/", include("applications.urls")),  # 报名表（前端使用别名）
    path("match/", include("applications.urls")),  # 匹配接口（前端使用）
    path("posts/", include("posts.urls")),  # 打卡表
    path("api/checkin/", include("posts.urls")),  # 打卡接口（前端使用）
    path("api/square/", include("posts.urls")),  # 广场接口（前端使用）
    path("tasks/", include("tasks.urls")),  # 打卡任务
    path("teams/", include("teams.urls")),  # 队伍
    path("users/", include("users.urls")),  # 用户
    path("upload/", include("users.urls")),  # 上传接口（头像和打卡图片，通过不同的子路径区分）
    # 健康检查与元信息（便于前端/运维探活与环境判断）
    path("health/", lambda request: JsonResponse({"status": "ok"})),
    path("meta/", lambda request: JsonResponse({
        "service": "zq_match_backend",
        "env": request.META.get("DJANGO_ENV", "development"),
    })),

    # OpenAPI/Swagger 文档（便于前端自动生成客户端 & Postman 导入）
    path("docs/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),  # swagger接口文档
    path(
            "docs/redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
    ),  # redoc接口文档
]

# 开发环境：提供media文件访问（仅DEBUG=True时）
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


