from academies.models import Academy
from academies.serializers import AcademySerializer
from rest_framework import mixins
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_extensions.cache.decorators import cache_response
from rest_framework_extensions.cache.mixins import CacheResponseMixin


class AcademyViewSet(
    CacheResponseMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    """
    院系信息
    """

    queryset = Academy.objects.all()
    serializer_class = AcademySerializer
    permission_classes = [AllowAny]  # 允许任何人访问
    pagination_class = None  # 禁用分页

    @cache_response(cache="default", timeout=60 * 60 * 1)
    def list(self, request, *args, **kwargs):
        """
        重写列表获取，返回所有院系的平级列表
        """
        # 获取所有顶层院系（parent=None）
        queryset = self.queryset.filter(parent=None).order_by('id')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
