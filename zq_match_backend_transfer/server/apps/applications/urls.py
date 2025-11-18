from rest_framework_extensions.routers import ExtendedSimpleRouter

from .views import ApplicationViewSet


router = ExtendedSimpleRouter()

urlpatterns = []

router.register(r"", ApplicationViewSet, basename="application")

urlpatterns += router.urls
