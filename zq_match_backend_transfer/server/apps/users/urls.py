from rest_framework import routers

from .views import UserView


router = routers.SimpleRouter()

urlpatterns = []

router.register(r"", UserView, basename="user")

urlpatterns += router.urls
