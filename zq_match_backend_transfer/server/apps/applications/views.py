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
from .serializers import ApplicationSerializer, SignupSerializer


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
        import logging
        from rest_framework.exceptions import ValidationError
        logger = logging.getLogger(__name__)
        
        try:
            # 检查用户是否已有报名表
            if Application.objects.filter(user=request.user).exists():
                raise ApiException(
                    ResponseType.ParamValidationFailed,
                    msg="您已提交过报名表，请勿重复提交",
                )
            
            logger.info(f"用户 {request.user.id} 提交报名数据: {request.data}")
            
            # 使用前端适配序列化器
            serializer = SignupSerializer(data=request.data, context={'request': request})
            
            # 验证数据，如果失败则提取友好的错误信息
            if not serializer.is_valid():
                # 提取字段级别的错误信息
                errors = serializer.errors
                error_messages = []
                
                # 遍历所有字段错误
                for field, field_errors in errors.items():
                    if isinstance(field_errors, list):
                        for error in field_errors:
                            # 提取错误消息
                            if hasattr(error, 'code'):
                                error_msg = str(error)
                            else:
                                error_msg = str(error)
                            error_messages.append(f"{self._get_field_label(field)}: {error_msg}")
                    else:
                        error_messages.append(f"{self._get_field_label(field)}: {str(field_errors)}")
                
                # 如果没有提取到具体错误，使用默认消息
                if not error_messages:
                    error_messages = [str(errors)]
                
                # 返回友好的错误信息
                raise ApiException(
                    ResponseType.ParamValidationFailed,
                    msg=error_messages[0] if len(error_messages) == 1 else "数据验证失败",
                    detail="; ".join(error_messages) if len(error_messages) > 1 else error_messages[0],
                    record=True,
                )
            
            application = serializer.save()
            
            logger.info(f"报名表创建成功: {application.id}")
            
            # 返回标准格式的序列化数据
            result_serializer = ApplicationSerializer(application, context={'request': request})
            headers = self.get_success_headers(result_serializer.data)
            return Response(result_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            
        except ApiException:
            raise
        except ValidationError as e:
            # DRF 的 ValidationError，提取错误信息
            error_messages = []
            if hasattr(e, 'detail'):
                if isinstance(e.detail, dict):
                    for field, field_errors in e.detail.items():
                        if isinstance(field_errors, list):
                            for error in field_errors:
                                error_messages.append(f"{self._get_field_label(field)}: {str(error)}")
                        else:
                            error_messages.append(f"{self._get_field_label(field)}: {str(field_errors)}")
                else:
                    error_messages.append(str(e.detail))
            else:
                error_messages.append(str(e))
            
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg=error_messages[0] if error_messages else "数据验证失败",
                detail="; ".join(error_messages) if len(error_messages) > 1 else (error_messages[0] if error_messages else str(e)),
                record=True,
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"创建报名表失败: {e}", exc_info=True)
            import traceback
            logger.error(f"错误堆栈: {traceback.format_exc()}")
            raise ApiException(
                ResponseType.ServerError,
                msg="提交报名失败",
                detail=str(e),
                record=True,
            )
    
    def _get_field_label(self, field_name):
        """获取字段的中文标签"""
        field_labels = {
            'name': '姓名',
            'gender': '性别',
            'degree': '学历',
            'studentNo': '学号',
            'majorCategory': '专业大类',
            'college': '院系',
            'qq': 'QQ号',
            'bio': '个人简介',
            'avatar': '头像',
            'signupType': '报名类型',
        }
        return field_labels.get(field_name, field_name)

    @action(methods=["get"], detail=False, url_path="my-application")
    def my_application(self, request):
        """获取我的报名表"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f"用户 {request.user.id} 请求报名表详情")
            
            # 优化查询：预加载 user 和关联数据
            application = Application.objects.select_related('user', 'my_academy').prefetch_related('academy_choice').filter(user=request.user).first()
            
            if not application:
                logger.info(f"用户 {request.user.id} 还没有报名表")
                raise ApiException(
                    ResponseType.ResourceNotFound,
                    msg="您还没有提交报名表",
                )
            
            logger.info(f"找到报名表 {application.id}，开始序列化")
            serializer = self.get_serializer(application, context={'request': request})
            logger.info(f"序列化成功，返回数据")
            return Response(serializer.data)
            
        except ApiException:
            raise
        except Exception as e:
            logger.error(f"获取报名表详情失败: {e}", exc_info=True)
            import traceback
            logger.error(f"错误堆栈: {traceback.format_exc()}")
            raise ApiException(
                ResponseType.ServerError,
                msg="获取报名表详情失败",
                detail=str(e),
                record=True,
            )
    
    @action(methods=["get"], detail=False, url_path="detail")
    def signup_detail(self, request):
        """获取我的报名表详情（前端使用）"""
        return self.my_application(request)

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

    @action(methods=["get"], detail=False, url_path="statistics")
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
