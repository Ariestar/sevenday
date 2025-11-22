from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Max, Case, When
from django.db import models
from django.utils import timezone

from server.utils.pagination import StandardResultsSetPagination
from .models import Post, PostLike, PostComment
from .serializers import PostSerializer, PostCreateSerializer
from tasks.models import Task
from users.serializers import UserSerializer
from zq_django_util.exceptions import ApiException
from zq_django_util.response import ResponseType


def get_photo_url(post, request):
    """获取并修正图片URL"""
    if not post or not post.photo:
        return None
    
    # 获取photo路径
    photo_path = post.photo.name if hasattr(post.photo, 'name') else str(post.photo)
    
    # 修正路径：如果路径中包含checkin/，替换为post/photo/
    if 'checkin/' in photo_path:
        # 提取文件名
        filename = photo_path.split('checkin/')[-1]
        photo_path = f"post/photo/{filename}"
    
    # 构建URL
    from django.conf import settings
    url_path = photo_path.replace('\\', '/')  # Windows路径转URL路径
    if not url_path.startswith('/'):
        url_path = '/' + url_path
    media_url = settings.MEDIA_URL.rstrip('/')
    return request.build_absolute_uri(f"{media_url}{url_path}")


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
        response_serializer = PostSerializer(post, context={'request': request})
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

    # ========== 前端打卡接口（/api/checkin/） ==========
    
    @action(methods=["get"], detail=False, url_path="tasks")
    def checkin_tasks(self, request):
        """获取打卡任务列表（20个任务）- 前端接口"""
        # 获取所有任务（按创建时间排序），最多20个
        tasks = Task.objects.all().order_by('create_time')[:20]
        
        result = []
        for idx, task in enumerate(tasks, start=1):
            result.append({
                'day': idx,
                'taskId': task.id,
                'title': task.title,
                'cover': request.build_absolute_uri(task.cover.url) if task.cover else None,
                'introduction': task.introduction,
                'score': task.score,
                'startTime': task.start_time.isoformat() if task.start_time else None,
                'endTime': task.end_time.isoformat() if task.end_time else None,
            })
        
        return Response(result)
    
    @action(methods=["post"], detail=False, url_path="submit")
    def checkin_submit(self, request):
        """提交打卡 - 前端接口"""
        user = request.user
        
        # 检查用户是否有队伍
        if not user.team:
            return Response(
                {"error": "您还没有队伍，无法打卡"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        day = request.data.get('day')
        task_id = request.data.get('taskId')  # 支持直接传递taskId
        
        if not day:
            return Response(
                {"error": "请提供day参数"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 如果提供了taskId，直接使用；否则根据day获取对应的任务
        if task_id:
            try:
                task = Task.objects.get(id=task_id)
            except Task.DoesNotExist:
                return Response(
                    {"error": f"任务ID {task_id} 不存在"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # 根据day获取对应的任务（假设任务按创建时间排序，第1个任务对应day=1）
            tasks = Task.objects.all().order_by('create_time')
            if day < 1 or day > tasks.count():
                return Response(
                    {"error": f"day参数无效，应在1-{tasks.count()}之间"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            task = tasks[day - 1]
        
        # 检查是否已经打卡：需要同时检查任务和天数
        # 因为同一个任务可以打卡多次（不同天数），所以需要检查title中是否包含"第{day}天"
        existing_post = Post.objects.filter(
            team=user.team,
            task=task,
            title__contains=f"第{day}天"
        ).first()
        
        if existing_post:
            return Response(
                {
                    "code": "00000",
                    "msg": "",
                    "detail": "",
                    "data": {
                        "error": f"该任务第{day}天已打卡",
                        "postId": existing_post.id,
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 处理前端数据格式
        content = request.data.get('content', '')
        images = request.data.get('images', [])
        sync_to_square = request.data.get('syncToSquare', False)  # 是否同步到广场
        
        # 检查是否有图片（可以是文件对象或URL字符串）
        photo_file = request.FILES.get('photo')  # 如果是文件上传
        photo_url = None
        
        if not photo_file and (not images or len(images) == 0):
            return Response(
                {
                    "code": "00000",
                    "msg": "",
                    "detail": "",
                    "data": {"photo": ["没有提交任何文件。"]}
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 如果前端传递的是图片URL数组，使用第一张
        if not photo_file and images and len(images) > 0:
            photo_url = images[0] if isinstance(images[0], str) else None
        
        # 创建打卡记录
        post_data = {
            'title': f"第{day}天打卡",
            'description': content,
            'task': task.id,
            'is_published': sync_to_square,  # 保存是否发布到广场
        }
        
        # 如果有文件对象，使用序列化器正常处理
        if photo_file:
            post_data['photo'] = photo_file
            serializer = PostCreateSerializer(data=post_data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            post = serializer.save(team=user.team, task=task)
        else:
            # 如果有图片URL，手动创建Post对象
            if photo_url:
                # 处理图片URL：提取相对路径并修正路径错误
                if photo_url.startswith('http'):
                    # 提取相对路径（假设URL格式为 http://host/media/...）
                    if '/media/' in photo_url:
                        relative_path = photo_url.split('/media/')[-1]
                    else:
                        # 如果URL格式不对，尝试提取文件名
                        relative_path = photo_url.split('/')[-1]
                else:
                    # 已经是相对路径
                    relative_path = photo_url
                
                # 修正路径：如果路径中包含checkin/，替换为post/photo/
                if 'checkin/' in relative_path:
                    # 提取文件名
                    filename = relative_path.split('checkin/')[-1]
                    relative_path = f"post/photo/{filename}"
                elif not relative_path.startswith('post/photo/'):
                    # 如果路径不是post/photo/开头，确保它是
                    if '/' in relative_path:
                        filename = relative_path.split('/')[-1]
                    else:
                        filename = relative_path
                    relative_path = f"post/photo/{filename}"
                
                # 创建Post对象，手动设置photo字段和is_published字段
                post = Post.objects.create(
                    title=post_data['title'],
                    description=post_data['description'],
                    photo=relative_path,  # 保存相对路径
                    team=user.team,
                    task=task,
                    is_published=sync_to_square  # 保存是否发布到广场
                )
            else:
                return Response(
                    {
                        "code": "00000",
                        "msg": "",
                        "detail": "",
                        "data": {"photo": ["没有提交任何文件。"]}
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        response_serializer = PostSerializer(post, context={'request': request})
        return Response(
            {
                "message": "打卡成功",
                "data": response_serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
    @action(methods=["get"], detail=False, url_path="checkin-detail")
    def checkin_detail(self, request):
        """获取某天的打卡详情 - 前端接口"""
        user = request.user
        day = request.query_params.get('day')
        
        if not day:
            return Response(
                {"code": "00000", "msg": "", "detail": "", "data": {"error": "请提供day参数"}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            day = int(day)
        except ValueError:
            return Response(
                {"error": "day参数必须是数字"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 根据day获取对应的任务
        tasks = Task.objects.all().order_by('create_time')
        if day < 1 or day > tasks.count():
            return Response(
                {"error": f"day参数无效，应在1-{tasks.count()}之间"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task = tasks[day - 1]
        
        # 获取我的打卡记录
        my_post = None
        if user.team:
            my_post = Post.objects.filter(
                team=user.team,
                task=task
            ).select_related('task', 'team').first()
        
        # 获取队友的打卡记录
        teammate_post = None
        if user.team and user.team.members.count() > 1:
            # 获取队伍中的其他成员
            teammates = user.team.members.exclude(id=user.id)
            if teammates.exists():
                # 假设队伍只有2个人，获取另一个人的打卡记录
                teammate = teammates.first()
                # 注意：这里需要根据实际业务逻辑来获取队友的打卡记录
                # 如果打卡是按队伍记录的，那么队友的打卡就是同一个Post
                # 如果打卡是按个人记录的，需要查询队友的Post
                pass
        
        result = {
            'day': day,
            'task': {
                'id': task.id,
                'title': task.title,
                'cover': request.build_absolute_uri(task.cover.url) if task.cover else None,
                'introduction': task.introduction,
                'score': task.score,
            },
            'myCheckin': PostSerializer(my_post, context={'request': request}).data if my_post else None,
            'teammateCheckin': PostSerializer(teammate_post, context={'request': request}).data if teammate_post else None,
        }
        
        return Response(result)
    
    @action(methods=["get"], detail=False, url_path="myList")
    def checkin_my_list(self, request):
        """获取我的打卡记录列表 - 前端接口"""
        user = request.user
        
        if not user.team:
            return Response([])
        
        posts = Post.objects.filter(team=user.team).select_related('task', 'team').order_by('-id')
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
    
    @action(methods=["get"], detail=False, url_path="teammateList")
    def checkin_teammate_list(self, request):
        """获取队友的打卡记录列表 - 前端接口"""
        user = request.user
        
        if not user.team:
            return Response([])
        
        # 注意：这里需要根据实际业务逻辑来获取队友的打卡记录
        # 如果打卡是按队伍记录的，那么队友的打卡就是同一个Post
        # 如果打卡是按个人记录的，需要查询队友的Post
        # 这里暂时返回空列表
        return Response([])
    
    @action(methods=["post"], detail=False, url_path="upload-image")
    def checkin_upload_image(self, request):
        """上传打卡图片 - 前端接口"""
        from zq_django_util.exceptions import ApiException
        from zq_django_util.response import ResponseType
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        import os
        import uuid
        from django.conf import settings
        
        # 兼容两种字段名：image 和 file（前端可能使用 file）
        image_file = request.FILES.get('image') or request.FILES.get('file')
        if not image_file:
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="请上传图片文件",
            )
        
        # 检查文件大小（限制5MB）
        if image_file.size > 5 * 1024 * 1024:
            raise ApiException(
                ResponseType.UnsupportedMediaSize,
                msg="图片大小不能超过5MB",
            )
        
        # 检查文件类型
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp']
        if image_file.content_type not in allowed_types:
            raise ApiException(
                ResponseType.UnsupportedMediaType,
                msg="只支持 JPG、PNG、WEBP 格式的图片",
            )
        
        # 生成唯一文件名：使用UUID + 原始文件扩展名
        original_name = image_file.name
        file_ext = os.path.splitext(original_name)[1].lower()
        if not file_ext:
            # 如果没有扩展名，根据content_type推断
            content_type_map = {
                'image/jpeg': '.jpg',
                'image/jpg': '.jpg',
                'image/png': '.png',
                'image/webp': '.webp',
            }
            file_ext = content_type_map.get(image_file.content_type, '.jpg')
        
        # 生成唯一文件名：post/photo/uuid.ext
        # 使用与Post模型相同的路径格式（post/photo）
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        upload_path = f"post/photo/{unique_filename}"
        
        # 保存文件
        try:
            # 读取文件内容
            file_content = image_file.read()
            # 使用default_storage保存文件
            saved_path = default_storage.save(upload_path, ContentFile(file_content))
            
            # 构建文件URL
            # 使用default_storage.url()方法获取URL（如果支持），否则手动构建
            try:
                photo_url = default_storage.url(saved_path)
            except (AttributeError, NotImplementedError):
                # 如果storage不支持url()方法，手动构建URL
                # saved_path通常是相对路径（相对于MEDIA_ROOT）
                # 需要转换为URL路径（使用正斜杠）
                url_path = saved_path.replace('\\', '/')  # Windows路径转URL路径
                if not url_path.startswith('/'):
                    url_path = '/' + url_path
                photo_url = f"{settings.MEDIA_URL.rstrip('/')}{url_path}"
            
            # 构建完整URL（包含域名）
            photo_url = request.build_absolute_uri(photo_url)
            
            return Response({
                "code": "00000",
                "msg": "图片上传成功",
                "data": {
                    "url": photo_url
                }
            })
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"保存打卡图片失败: {str(e)}", exc_info=True)
            raise ApiException(
                ResponseType.InternalServerError,
                msg=f"图片保存失败: {str(e)}",
            )
    
    @action(methods=["post"], detail=False, url_path="resubmit")
    def checkin_resubmit(self, request):
        """重新提交打卡（被驳回后）- 前端接口"""
        user = request.user
        checkin_id = request.data.get('checkinId')
        
        if not checkin_id:
            return Response(
                {"error": "请提供checkinId参数"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            post = Post.objects.get(id=checkin_id)
        except Post.DoesNotExist:
            return Response(
                {"error": "打卡记录不存在"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 检查权限：只能修改自己队伍的打卡
        if post.team != user.team:
            return Response(
                {"error": "无权修改其他队伍的打卡记录"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 更新打卡记录
        content = request.data.get('content', '')
        images = request.data.get('images', [])
        
        if content:
            post.description = content
        
        # 处理图片更新（需要根据实际业务逻辑处理）
        
        post.save()
        
        serializer = PostSerializer(post, context={'request': request})
        return Response(
            {
                "message": "重新提交成功",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    # ========== 广场相关接口（/api/square/） ==========
    
    @action(methods=["get"], detail=False, url_path="list")
    def square_list(self, request):
        """获取广场列表（分页的打卡记录）- 前端接口"""
        try:
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('pageSize', 20))
            sort_type = request.query_params.get('sort', 'latest')  # latest: 最新发布, comment: 最新评论
            
            # 只获取发布到广场的打卡记录
            queryset = Post.objects.filter(is_published=True).select_related('task', 'team').prefetch_related('likes', 'comments')
            
            # 根据排序类型排序
            if sort_type == 'comment':
                # 按最新评论时间排序：使用 Max 聚合获取每条打卡的最新评论时间
                # 对于没有评论的打卡，latest_comment_time 为 None，会排在最后
                queryset = queryset.annotate(
                    latest_comment_time=Max('comments__create_time')
                ).order_by(
                    '-latest_comment_time',  # 先按最新评论时间倒序（None 会排在最后）
                    '-create_time'  # 如果评论时间相同或为 None，按创建时间倒序
                )
            else:
                # 默认按最新发布排序
                queryset = queryset.order_by('-create_time')
            
            # 手动分页
            start = (page - 1) * page_size
            end = start + page_size
            posts = queryset[start:end]
        except Exception as e:
            import traceback
            error_msg = f"获取广场列表失败: {str(e)}\n{traceback.format_exc()}"
            raise ApiException(
                ResponseType.InternalServerError,
                msg=error_msg,
            )
        
        result = []
        user = request.user
        
        for post in posts:
            # 检查当前用户是否已点赞
            is_liked = False
            if user.is_authenticated:
                is_liked = PostLike.objects.filter(post=post, user=user).exists()
            
            # 获取点赞数
            like_count = post.likes.count()
            
            # 获取评论数
            comment_count = post.comments.count()
            
            # 构建图片URL（修正路径错误）
            photo_url = get_photo_url(post, request)
            
            result.append({
                'postId': post.id,
                'title': post.title,
                'content': post.description,
                'photo': photo_url,
                'teamName': post.team.name if post.team else None,
                'taskTitle': post.task.title if post.task else None,
                'likeCount': like_count,
                'commentCount': comment_count,
                'viewCount': post.view_count,
                'isLiked': is_liked,
                'createTime': post.create_time.isoformat() if post.create_time else None,
            })
        
        return Response({
            'list': result,
            'page': page,
            'pageSize': page_size,
            'total': queryset.count(),
        })
    
    @action(methods=["post"], detail=False, url_path="like")
    def square_like(self, request):
        """点赞/取消点赞 - 前端接口"""
        user = request.user
        post_id = request.data.get('postId')
        
        if not post_id:
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="请提供postId参数",
            )
        
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise ApiException(
                ResponseType.ResourceNotFound,
                msg="打卡记录不存在",
            )
        
        # 检查是否已点赞
        like, created = PostLike.objects.get_or_create(post=post, user=user)
        
        if created:
            # 新点赞
            return Response({
                'msg': '点赞成功',
                'isLiked': True,
                'likeCount': post.likes.count(),
            })
        else:
            # 取消点赞
            like.delete()
            return Response({
                'msg': '取消点赞成功',
                'isLiked': False,
                'likeCount': post.likes.count(),
            })
    
    @action(methods=["get"], detail=False, url_path="detail")
    def square_detail(self, request):
        """获取广场详情（打卡详情）- 前端接口"""
        # 优先检查postId参数（广场详情使用）
        post_id = request.query_params.get('postId')
        
        # 如果没有postId但有day参数，说明可能是误路由到checkin_detail
        # 这种情况下应该返回错误，提示使用postId
        if not post_id:
            day = request.query_params.get('day')
            if day:
                raise ApiException(
                    ResponseType.ParamValidationFailed,
                    msg="广场详情接口需要使用postId参数，而不是day参数",
                )
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="请提供postId参数",
            )
        
        try:
            post = Post.objects.select_related('task', 'team').prefetch_related('likes', 'comments', 'comments__user').get(id=post_id)
        except Post.DoesNotExist:
            raise ApiException(
                ResponseType.ResourceNotFound,
                msg="打卡记录不存在",
            )
        
        # 增加浏览量（使用 F() 避免并发问题）
        from django.db.models import F
        Post.objects.filter(id=post_id).update(view_count=F('view_count') + 1)
        post.refresh_from_db()  # 刷新对象以获取最新的浏览量
        
        user = request.user
        
        # 检查当前用户是否已点赞
        is_liked = False
        if user.is_authenticated:
            is_liked = PostLike.objects.filter(post=post, user=user).exists()
        
        # 获取点赞列表（前10个）
        likes = post.likes.select_related('user')[:10]
        like_users = [{'userId': like.user.id, 'username': like.user.username, 'avatar': request.build_absolute_uri(like.user.avatar.url) if like.user.avatar else None} for like in likes]
        
        # 获取评论列表（按时间正序，最早的在前面）
        comments = post.comments.select_related('user').order_by('create_time')
        comment_list = []
        for comment in comments:
            # 确保评论内容不为空
            comment_content = comment.content if comment.content else ''
            comment_list.append({
                'commentId': comment.id,
                'userId': comment.user.id,
                'username': comment.user.username or '匿名用户',
                'avatar': request.build_absolute_uri(comment.user.avatar.url) if comment.user.avatar else None,
                'content': comment_content,  # 确保评论内容字段存在
                'createTime': comment.create_time.isoformat() if comment.create_time else None,
            })
        
        # 构建图片URL（修正路径错误）
        photo_url = get_photo_url(post, request)
        
        return Response({
            'postId': post.id,
            'title': post.title,
            'content': post.description,
            'photo': photo_url,
            'teamName': post.team.name if post.team else None,
            'taskTitle': post.task.title if post.task else None,
            'likeCount': post.likes.count(),
            'commentCount': post.comments.count(),
            'viewCount': post.view_count,
            'isLiked': is_liked,
            'likeUsers': like_users,
            'comments': comment_list,
            'createTime': post.create_time.isoformat() if post.create_time else None,
        })
    
    @action(methods=["post"], detail=False, url_path="comment")
    def square_comment(self, request):
        """提交评论 - 前端接口"""
        user = request.user
        post_id = request.data.get('postId')
        content = request.data.get('content', '').strip()
        
        if not post_id:
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="请提供postId参数",
            )
        
        if not content:
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="评论内容不能为空",
            )
        
        if len(content) > 500:
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="评论内容不能超过500个字符",
            )
        
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise ApiException(
                ResponseType.ResourceNotFound,
                msg="打卡记录不存在",
            )
        
        # 创建评论
        comment = PostComment.objects.create(
            post=post,
            user=user,
            content=content
        )
        
        # 确保评论内容不为空
        comment_content = comment.content if comment.content else ''
        
        return Response({
            'msg': '评论成功',
            'commentId': comment.id,
            'comment': {
                'commentId': comment.id,
                'userId': comment.user.id,
                'username': comment.user.username or '匿名用户',
                'avatar': request.build_absolute_uri(comment.user.avatar.url) if comment.user.avatar else None,
                'content': comment_content,  # 确保评论内容字段存在
                'createTime': comment.create_time.isoformat() if comment.create_time else None,
            },
            'commentCount': post.comments.count(),
        })
    
    @action(methods=["get"], detail=False, url_path="share")
    def square_share(self, request):
        """获取分享链接 - 前端接口"""
        post_id = request.query_params.get('postId')
        
        if not post_id:
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="请提供postId参数",
            )
        
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise ApiException(
                ResponseType.ResourceNotFound,
                msg="打卡记录不存在",
            )
        
        # 构建分享链接（使用前端页面路径）
        # 假设前端路由为 /pages/square-detail/index?postId=xxx
        share_url = f"{request.scheme}://{request.get_host()}/pages/square-detail/index?postId={post_id}"
        
        return Response({
            'shareUrl': share_url,
            'postId': post.id,
            'title': post.title,
            'photo': get_photo_url(post, request),
        })