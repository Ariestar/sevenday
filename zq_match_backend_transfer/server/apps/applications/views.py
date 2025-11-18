from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q
from zq_django_util.exceptions import ApiException
from zq_django_util.response import ResponseType

from teams.models import Team
from users.models import User
from users.serializers import UserSerializer
from server.utils.pagination import StandardResultsSetPagination
from .match import match, DAILY_ATTEMPT_LIMIT
from .models import MatchAttempt
from .models import Application
from .serializers import ApplicationSerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    """报名表视图集"""
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """权限管理：普通用户只能看到自己的报名表"""
        queryset = super().get_queryset()
        
        # 优化查询性能
        queryset = queryset.select_related('user', 'my_academy').prefetch_related('academy_choice')
        
        if self.request.user.is_staff:
            return queryset
        else:
            return queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """创建报名表"""
        # 检查用户是否已有报名表
        if Application.objects.filter(user=request.user).exists():
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="您已提交过报名表，请勿重复提交",
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=["get"], detail=False, url_path="my-application")
    def my_application(self, request):
        """获取我的报名表"""
        application = Application.objects.filter(user=request.user).first()
        if not application:
            raise ApiException(
                ResponseType.ResourceNotFound,
                msg="您还没有提交报名表",
            )
        serializer = self.get_serializer(application)
        return Response(serializer.data)

    @action(methods=["get"], detail=False, url_path="match-status")
    def match_status(self, request):
        """查询匹配状态"""
        user = request.user
        data = {
            "is_match": user.is_match,
            "team_id": user.team_id if user.team else None,
        }
        
        if user.is_match and user.team:
            # 获取队友信息
            teammates = User.objects.filter(team=user.team).exclude(id=user.id)
            data["teammates"] = UserSerializer(teammates, many=True).data
        
        return Response(data)

    @action(methods=["post"], detail=False, url_path="rematch")
    def rematch(self, request):
        """执行匹配"""
        user = request.user
        
        # 检查是否有报名表
        if not Application.objects.filter(user=user).exists():
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="请先提交报名表",
            )
        
        # 如果已经匹配，返回当前队友信息
        if user.is_match and user.team:
            teammates = User.objects.filter(team=user.team).exclude(id=user.id)
            return Response({
                "msg": "您已经匹配成功",
                "teammates": UserSerializer(teammates, many=True).data
            })
        # 执行匹配（保留原行为：直接尝试匹配并建队）
        match_user = match(user.id, enforce_limit=True)

        if match_user is None:
            raise ApiException(
                ResponseType.ResourceNotFound,
                msg="暂时没有找到合适的匹配对象，请稍后再试",
            )

        return Response({
            "msg": "匹配成功",
            "teammate": UserSerializer(match_user).data
        })

    @action(methods=["post"], detail=False, url_path="self-match")
    def self_match(self, request):
        """
        自助匹配：允许用户随时触发匹配
        - 每日最多尝试 DAILY_ATTEMPT_LIMIT 次
        - 未提交报名表、已在队伍、或达到次数限制则直接返回提示
        """
        user = request.user

        # 报名检查
        if not Application.objects.filter(user=user).exists():
            raise ApiException(ResponseType.ParamValidationFailed, msg="请先提交报名表")

        # 状态检查
        if user.is_match and user.team:
            teammates = User.objects.filter(team=user.team).exclude(id=user.id)
            return Response({
                "msg": "您已经匹配成功",
                "teammates": UserSerializer(teammates, many=True).data
            })

        # 次数限制
        from django.utils import timezone
        start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = start.replace(hour=23, minute=59, second=59, microsecond=999999)
        today_times = MatchAttempt.objects.filter(user=user, created_at__range=(start, end)).count()
        if today_times >= DAILY_ATTEMPT_LIMIT:
            return Response({
                "msg": f"今日匹配次数已达上限({DAILY_ATTEMPT_LIMIT})，请明天再试",
                "today_attempts": today_times,
                "limit": DAILY_ATTEMPT_LIMIT,
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        match_user = match(user.id, enforce_limit=False)  # 由视图层自行做限制
        if match_user is None:
            return Response({
                "msg": "暂未找到合适对象，请稍后再试",
                "today_attempts": today_times + 1,
                "limit": DAILY_ATTEMPT_LIMIT,
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "msg": "匹配成功",
            "teammate": UserSerializer(match_user).data,
            "today_attempts": today_times + 1,
            "limit": DAILY_ATTEMPT_LIMIT,
        }, status=status.HTTP_200_OK)

    @action(methods=["get"], detail=False, url_path="self-match/status")
    def self_match_status(self, request):
        """今日自助匹配次数与状态查询"""
        user = request.user
        from django.utils import timezone
        start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = start.replace(hour=23, minute=59, second=59, microsecond=999999)
        today_times = MatchAttempt.objects.filter(user=user, created_at__range=(start, end)).count()
        return Response({
            "is_matched": user.is_match,
            "team_id": user.team_id if user.team else None,
            "today_attempts": today_times,
            "limit": DAILY_ATTEMPT_LIMIT,
        })

    @action(methods=["get"], detail=False, url_path="statistics", permission_classes=[IsAuthenticated])
    def statistics(self, request):
        """报名统计信息（管理员可查看全部，用户只能看自己的）"""
        if request.user.is_staff:
            # 管理员看全局统计
            total_applications = Application.objects.count()
            matched_users = User.objects.filter(is_match=True).count()
            
            # 按院系统计
            from django.db.models import Count
            academy_stats = Application.objects.values(
                'my_academy__name'
            ).annotate(
                count=Count('id')
            ).order_by('-count')
            
            # 按性别统计
            gender_stats = Application.objects.values(
                'my_gender'
            ).annotate(
                count=Count('id')
            )
            
            return Response({
                'total_applications': total_applications,
                'matched_users': matched_users,
                'match_rate': round(matched_users / total_applications * 100, 2) if total_applications > 0 else 0,
                'academy_distribution': list(academy_stats),
                'gender_distribution': list(gender_stats),
            })
        else:
            # 普通用户只能看到自己的状态
            has_application = Application.objects.filter(user=request.user).exists()
            return Response({
                'has_application': has_application,
                'is_matched': request.user.is_match,
                'team_id': request.user.team_id if request.user.team else None,
            })
