from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.utils import timezone

from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    """任务视图集"""
    queryset = Task.objects.order_by("-id")
    serializer_class = TaskSerializer

    def get_permissions(self):
        """权限控制：查看任务需要登录，创建/修改/删除需要管理员权限"""
        if self.action in ["list", "retrieve", "active_tasks", "my_tasks", "upcoming_tasks"]:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    @action(methods=["get"], detail=False, url_path="active")
    def active_tasks(self, request):
        """获取进行中的任务"""
        now = timezone.now().date()
        tasks = Task.objects.filter(
            start_time__lte=now,
            end_time__gte=now
        ).order_by('end_time')
        
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(methods=["get"], detail=False, url_path="my-completed")
    def my_tasks(self, request):
        """获取我的队伍已完成的任务"""
        user = request.user
        if not user.team:
            return Response([])
        
        completed_tasks = user.team.task.all()
        serializer = self.get_serializer(completed_tasks, many=True)
        return Response(serializer.data)

    @action(methods=["get"], detail=False, url_path="upcoming")
    def upcoming_tasks(self, request):
        """获取即将开始的任务"""
        now = timezone.now().date()
        tasks = Task.objects.filter(
            start_time__gt=now
        ).order_by('start_time')[:5]
        
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
