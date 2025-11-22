from rest_framework import routers
from django.urls import path

from .views import UserView
from posts.views import PostViewSet


router = routers.SimpleRouter()

urlpatterns = []

router.register(r"", UserView, basename="user")

# 上传接口（前端使用 /upload/ 路径）
# 这些路由会在 server/urls.py 中通过 path("upload/", include("users.urls")) 映射
urlpatterns += [
    path("avatar", UserView.as_view({'post': 'upload_avatar'}), name="upload-avatar"),
    path("checkin", PostViewSet.as_view({'post': 'checkin_upload_image'}), name="upload-checkin"),
]

urlpatterns += router.urls
