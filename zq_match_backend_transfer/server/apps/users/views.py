from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Count
from zq_django_util.exceptions import ApiException
from zq_django_util.response import ResponseType

from server.utils.pagination import StandardResultsSetPagination
from .models import User
from .serializers import UserInfoSerializer, UserSerializer, ChangePasswordSerializer


class UserView(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.DestroyModelMixin,
):
    """用户信息视图"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'school_number']
    ordering_fields = ['id', 'create_time', 'grade']
    ordering = ['-id']

    def get_permissions(self):
        if self.action in ["destroy", "list_all", "user_statistics"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """权限控制：普通用户只能访问自己的信息"""
        queryset = super().get_queryset()
        
        # 优化查询性能
        queryset = queryset.select_related('academy', 'team')
        
        if self.action in ["list", "update", "me"]:
            return queryset.filter(id=self.request.user.id)
        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return UserInfoSerializer
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        """获取当前用户信息"""
        instance = self.get_queryset().first()
        if not instance:
            raise ApiException(
                ResponseType.ResourceNotFound,
                msg="用户不存在",
            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(methods=["get"], detail=False, url_path="me")
    def me(self, request):
        """获取当前用户详细信息"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(methods=["patch"], detail=False, url_path="update-profile")
    def update_profile(self, request):
        """更新个人资料"""
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(methods=["post"], detail=False, url_path="change-password")
    def change_password(self, request):
        """修改密码"""
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        
        # 验证旧密码
        if not user.check_password(serializer.validated_data['old_password']):
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="旧密码错误",
            )
        
        # 设置新密码
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            "msg": "密码修改成功，请重新登录"
        })

    @action(methods=["post"], detail=False, url_path="upload-avatar")
    def upload_avatar(self, request):
        """上传头像"""
        if 'avatar' not in request.FILES:
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="请上传头像文件",
            )
        
        user = request.user
        serializer = self.get_serializer(
            user,
            data={'avatar': request.FILES['avatar']},
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            "msg": "头像上传成功",
            "avatar": serializer.data['avatar']
        })

    @action(methods=["get"], detail=False, url_path="list-all", permission_classes=[IsAdminUser])
    def list_all(self, request):
        """管理员查看所有用户"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=["get"], detail=False, url_path="user-statistics", permission_classes=[IsAdminUser])
    def user_statistics(self, request):
        """用户统计信息（管理员）"""
        total_users = User.objects.count()
        matched_users = User.objects.filter(is_match=True).count()
        
        # 按院系统计
        academy_stats = User.objects.values(
            'academy__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        # 按年级统计
        grade_stats = User.objects.values(
            'grade'
        ).annotate(
            count=Count('id')
        ).order_by('-grade')
        
        # 按性别统计
        gender_stats = User.objects.values(
            'gender'
        ).annotate(
            count=Count('id')
        )
        
        return Response({
            'total_users': total_users,
            'matched_users': matched_users,
            'unmatched_users': total_users - matched_users,
            'match_rate': round(matched_users / total_users * 100, 2) if total_users > 0 else 0,
            'academy_distribution': list(academy_stats),
            'grade_distribution': list(grade_stats),
            'gender_distribution': list(gender_stats),
        })
