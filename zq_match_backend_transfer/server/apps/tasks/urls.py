from rest_framework import routers

from .views import TaskViewSet


router = routers.SimpleRouter()

urlpatterns = []

router.register(r"", TaskViewSet, basename="task")

urlpatterns += router.urls
