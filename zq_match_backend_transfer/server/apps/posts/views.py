from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone

from server.utils.pagination import StandardResultsSetPagination
from .models import Post
from .serializers import PostSerializer, PostCreateSerializer
from tasks.models import Task


class PostViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.CreateModelMixin,
):
    """打卡记录视图集"""
    queryset = Post.objects.all().order_by('-id')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['task', 'team']
    ordering_fields = ['id']
    ordering = ['-id']
    search_fields = ['title', 'description', 'team__name']

    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action == 'create':
            return PostCreateSerializer
        return PostSerializer

    def get_queryset(self):
        """优化查询性能"""
        queryset = super().get_queryset()
        return queryset.select_related('task', 'team')
    
    def create(self, request, *args, **kwargs):
        """创建打卡记录"""
        user = request.user
        
        # 检查用户是否有队伍
        if not user.team:
            return Response(
                {"error": "您还没有队伍，无法打卡"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查任务是否存在
        task_id = request.data.get('task')
        if not task_id:
            return Response(
                {"error": "请提供任务ID"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response(
                {"error": "任务不存在"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 检查任务时间
        now = timezone.now()
        if now < task.start_time:
            return Response(
                {"error": f"任务还未开始，开始时间：{task.start_time}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if now > task.end_time:
            return Response(
                {"error": f"任务已结束，结束时间：{task.end_time}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查是否已经打卡
        existing_post = Post.objects.filter(
            team=user.team,
            task=task
        ).first()
        
        if existing_post:
            return Response(
                {
                    "error": "该任务已打卡",
                    "post_id": existing_post.id,
                    "created_at": existing_post.id
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 创建打卡记录
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save(team=user.team, task=task)
        
        # 返回完整信息
        response_serializer = PostSerializer(post)
        return Response(
            {
                "message": "打卡成功",
                "post": response_serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    @action(methods=["get"], detail=False, url_path="my-posts")
    def my_posts(self, request):
        """获取我的队伍的打卡记录"""
        user = request.user
        if not user.team:
            return Response({"results": [], "count": 0})
        
        posts = Post.objects.filter(team=user.team).select_related('task', 'team').order_by('-id')
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
    
    @action(methods=["get"], detail=False, url_path="check-status")
    def check_status(self, request):
        """检查某个任务是否已打卡"""
        user = request.user
        task_id = request.query_params.get('task_id')
        
        if not user.team:
            return Response(
                {"error": "您还没有队伍"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not task_id:
            return Response(
                {"error": "请提供task_id参数"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查是否已打卡
        post = Post.objects.filter(
            team=user.team,
            task_id=task_id
        ).select_related('task', 'team').first()
        
        if post:
            serializer = self.get_serializer(post)
            return Response({
                "checked": True,
                "post": serializer.data
            })
        else:
            return Response({
                "checked": False,
                "post": None
            })
    
    @action(methods=["delete"], detail=True, url_path="delete-post")
    def delete_post(self, request, pk=None):
        """删除打卡记录（仅限本队伍）"""
        user = request.user
        
        try:
            post = Post.objects.get(id=pk)
        except Post.DoesNotExist:
            return Response(
                {"error": "打卡记录不存在"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 检查权限：只能删除自己队伍的打卡
        if post.team != user.team:
            return Response(
                {"error": "无权删除其他队伍的打卡记录"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 检查任务是否已结束
        if timezone.now() > post.task.end_time:
            return Response(
                {"error": "任务已结束，无法删除打卡记录"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        post.delete()
        return Response(
            {"message": "打卡记录已删除"},
            status=status.HTTP_200_OK
        )

    @action(methods=["get"], detail=False, url_path="by-task")
    def by_task(self, request):
        """按任务查看打卡记录"""
        task_id = request.query_params.get('task_id')
        if not task_id:
            return Response({"error": "请提供task_id参数"}, status=400)
        
        posts = Post.objects.filter(task_id=task_id).order_by('-id')
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
