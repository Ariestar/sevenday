from rest_framework import routers

from .views import PostViewSet


router = routers.SimpleRouter()

urlpatterns = []

router.register(r"", PostViewSet, basename="post")

urlpatterns += router.urls
