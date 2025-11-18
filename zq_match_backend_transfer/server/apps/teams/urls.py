from rest_framework import routers

from .views import TeamViewSet


router = routers.SimpleRouter()

urlpatterns = []

router.register(r"", TeamViewSet, basename="team")

urlpatterns += router.urls
