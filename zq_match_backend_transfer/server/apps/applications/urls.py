from rest_framework_extensions.routers import ExtendedSimpleRouter
from django.urls import path

from .views import ApplicationViewSet
from .match_views import MatchViewSet


router = ExtendedSimpleRouter()

urlpatterns = []

router.register(r"", ApplicationViewSet, basename="application")

# 匹配接口路由（前端使用 /match/ 路径）
# 注意：这些路由会在 server/urls.py 中通过 path("match/", include("applications.urls")) 映射
urlpatterns += [
    path("auto/", MatchViewSet.as_view({'post': 'auto_match'}), name="match-auto"),
    path("target/", MatchViewSet.as_view({'post': 'target_match'}), name="match-target"),
    path("confirm/", MatchViewSet.as_view({'post': 'confirm_match'}), name="match-confirm"),
    path("list/", MatchViewSet.as_view({'get': 'match_list'}), name="match-list"),
    path("team/", MatchViewSet.as_view({'get': 'get_team_info'}), name="match-team"),
    path("teamName/", MatchViewSet.as_view({'post': 'set_team_name'}), name="match-team-name"),
    path("disband/", MatchViewSet.as_view({'post': 'disband_team'}), name="match-disband"),
    path("checkDisband/", MatchViewSet.as_view({'get': 'check_disband_permission'}), name="match-check-disband"),
    path("expectation/", MatchViewSet.as_view({'get': 'match_expectation', 'post': 'match_expectation'}), name="match-expectation"),
    path("recommend/", MatchViewSet.as_view({'post': 'recommend'}), name="match-recommend"),
    path("reject/", MatchViewSet.as_view({'post': 'reject_match'}), name="match-reject"),
    path("invitation/", MatchViewSet.as_view({'get': 'get_invitation'}), name="match-invitation"),
    path("exchange/", MatchViewSet.as_view({'get': 'get_exchange_request', 'post': 'request_exchange'}), name="match-exchange"),
    path("exchange/respond/", MatchViewSet.as_view({'post': 'respond_exchange'}), name="match-exchange-respond"),
]

urlpatterns += router.urls
