from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.db.models import Count, Q
from zq_django_util.exceptions import ApiException
from zq_django_util.response import ResponseType

from posts.models import Post
from posts.serializers import PostSerializer
from tasks.models import Task
from users.models import User
from server.utils.pagination import StandardResultsSetPagination
from .models import Team
from .serializers import TeamSerializer, TeamInfoSerializer


class TeamViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.DestroyModelMixin,
):
    """队伍视图集"""
    queryset = Team.objects.order_by("-score")
    serializer_class = TeamSerializer
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action in ["list", "retrieve", "my_team"]:
            return TeamInfoSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """优化查询性能"""
        queryset = super().get_queryset()
        
        # 预加载关联数据
        if self.action in ["list", "retrieve", "my_team"]:
            queryset = queryset.prefetch_related('users', 'task')
        
        if self.action == "update":
            # 更新时只能操作自己的队伍
            user = self.request.user
            if user.team:
                return queryset.filter(id=user.team.id)
            return Team.objects.none()
        
        return queryset

    @action(methods=["get"], detail=False, url_path="my-team")
    def my_team(self, request):
        """获取我的队伍信息"""
        user = request.user
        if not user.team:
            raise ApiException(
                ResponseType.ResourceNotFound,
                msg="您还没有加入队伍",
            )
        
        serializer = self.get_serializer(user.team)
        return Response(serializer.data)

    @action(methods=["post"], detail=False, url_path="disband")
    def disband(self, request):
        """解散队伍"""
        user = request.user
        if not user.team:
            raise ApiException(
                ResponseType.ResourceNotFound,
                msg="您还没有加入队伍",
            )
        
        team = user.team
        
        # 将队伍成员的状态重置
        members = User.objects.filter(team=team)
        members.update(is_match=False, team=None)
        
        # 删除队伍
        team.delete()
        
        return Response({
            "msg": "队伍已解散"
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """删除队伍（管理员）"""
        team = self.get_object()
        
        # 将队伍成员的状态重置
        members = User.objects.filter(team=team)
        members.update(is_match=False, team=None)
        
        # 删除队伍
        self.perform_destroy(team)
        
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["post"], detail=True, url_path="complete-task")
    def complete_task(self, request, pk=None):
        """完成任务并提交打卡"""
        user = request.user
        
        # 验证用户是否有队伍
        if not user.team:
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="您还没有加入队伍",
            )
        
        team = user.team
        
        # 验证任务是否存在
        try:
            task = Task.objects.get(id=pk)
        except Task.DoesNotExist:
            raise ApiException(
                ResponseType.ResourceNotFound,
                msg="任务不存在",
            )
        
        # 验证任务是否已完成
        if team.task.filter(id=task.id).exists():
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="该任务已完成",
            )
        
        # 验证必要字段
        if 'title' not in request.data or 'description' not in request.data:
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="请提供标题和描述",
            )
        
        if 'photo' not in request.FILES:
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="请上传打卡照片",
            )
        
        # 创建打卡记录
        post = Post.objects.create(
            title=request.data["title"],
            description=request.data["description"],
            photo=request.FILES["photo"],
            team=team,
            task=task,
        )
        
        # 添加任务到队伍的完成列表
        team.task.add(task)
        
        # 更新队伍分数
        team.score += task.score
        team.save()
        
        serializer = PostSerializer(post)
        return Response({
            "msg": "任务完成",
            "post": serializer.data,
            "current_score": team.score,
        }, status=status.HTTP_201_CREATED)

    @action(methods=["get"], detail=False, url_path="statistics")
    def statistics(self, request):
        """队伍统计信息"""
        # 总队伍数
        total_teams = Team.objects.count()
        
        # 有任务完成的队伍数
        active_teams = Team.objects.filter(task__isnull=False).distinct().count()
        
        # 平均分数
        from django.db.models import Avg
        avg_score = Team.objects.aggregate(Avg('score'))['score__avg'] or 0
        
        # 最高分队伍
        top_team = Team.objects.order_by('-score').first()
        top_team_data = None
        if top_team:
            top_team_data = {
                'id': top_team.id,
                'name': top_team.name,
                'score': top_team.score,
            }
        
        return Response({
            'total_teams': total_teams,
            'active_teams': active_teams,
            'average_score': round(avg_score, 2),
            'top_team': top_team_data,
        })
