"""
匹配相关接口视图集（前端使用 /match/ 路径）
"""
import re
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from zq_django_util.exceptions import ApiException
from zq_django_util.response import ResponseType

from teams.models import Team
from teams.serializers import TeamInfoSerializer
from users.models import User
from users.serializers import UserSerializer
from .match import match, recommend_matches, DAILY_ATTEMPT_LIMIT
from .models import MatchAttempt, Application, TeamInvitation, TeamExchangeRequest
from .serializers import MatchExpectationSerializer
from academies.models import Academy
from .models import TeamExchangeRequest


class MatchViewSet(viewsets.GenericViewSet):
    """匹配相关接口视图集（前端使用）"""
    permission_classes = [IsAuthenticated]

    @action(methods=["post"], detail=False, url_path="recommend")
    def recommend(self, request):
        """获取推荐匹配对象列表（不直接组队）"""
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
                "code": "00000",
                "msg": "您已经匹配成功",
                "data": {
                    "recommendations": [],
                    "isMatched": True,
                    "teammates": UserSerializer(teammates, many=True).data,
                    "team": TeamInfoSerializer(user.team).data if user.team else None,
                }
            })
        
        # 获取推荐列表
        limit = request.data.get('limit', 10)
        recommendations = recommend_matches(user.id, limit=limit)
        
        # 序列化推荐结果
        recommendations_data = []
        for rec in recommendations:
            user_data = UserSerializer(rec['user']).data
            user_data['matchScore'] = rec['score']
            recommendations_data.append(user_data)
        
        return Response({
            "code": "00000",
            "msg": "",
            "data": {
                "recommendations": recommendations_data,
                "isMatched": False,
            }
        })

    @action(methods=["post"], detail=False, url_path="auto")
    def auto_match(self, request):
        """系统自动匹配"""
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
                "code": "00000",
                "msg": "您已经匹配成功",
                "data": {
                    "teammates": UserSerializer(teammates, many=True).data,
                    "team": TeamInfoSerializer(user.team).data if user.team else None,
                }
            })
        
        # 执行匹配
        match_user = match(user.id, enforce_limit=True)
        
        if match_user is None:
            raise ApiException(
                ResponseType.ResourceNotFound,
                msg="暂时没有找到合适的匹配对象，请稍后再试",
            )
        
        return Response({
            "code": "00000",
            "msg": "匹配成功",
            "data": {
                "teammate": UserSerializer(match_user).data,
                "team": TeamInfoSerializer(user.team).data if user.team else None,
            }
        })

    @action(methods=["post"], detail=False, url_path="target")
    def target_match(self, request):
        """定向匹配（通过学号）"""
        user = request.user
        student_no = request.data.get('studentNo')
        
        if not student_no:
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="请提供学号",
            )
        
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
                "code": "00000",
                "msg": "您已经匹配成功",
                "data": {
                    "teammates": UserSerializer(teammates, many=True).data,
                }
            })
        
        # 查找目标用户（支持学号或用户名）
        student_no = student_no.strip()
        target_user = None
        
        if not student_no:
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="学号或用户名不能为空",
            )
        
        # 先尝试通过学号查找（排除空字符串）
        try:
            target_user = User.objects.get(school_number=student_no)
        except User.DoesNotExist:
            pass
        except User.MultipleObjectsReturned:
            # 如果学号有重复，取第一个
            target_user = User.objects.filter(school_number=student_no).first()
        
        # 如果通过学号找不到，尝试通过用户名查找
        if not target_user:
            try:
                target_user = User.objects.get(username=student_no)
            except User.DoesNotExist:
                pass
            except User.MultipleObjectsReturned:
                # 如果用户名有重复，取第一个
                target_user = User.objects.filter(username=student_no).first()
        
        # 如果还是找不到，返回错误
        if not target_user:
            # 记录调试信息
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"用户 {user.id} 尝试匹配，但未找到学号/用户名 '{student_no}' 对应的用户")
            
            raise ApiException(
                ResponseType.ResourceNotFound,
                msg=f"未找到学号或用户名 '{student_no}' 对应的用户，请确认输入是否正确",
            )
        
        
        # 检查是否是自己（防止自己邀请自己）
        if target_user.id == user.id:
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="不能邀请自己组队",
            )
        
        # 检查目标用户是否已匹配
        if target_user.is_match:
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="该用户已匹配",
            )
        
        # 检查目标用户是否有报名表
        if not Application.objects.filter(user=target_user).exists():
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="目标用户尚未提交报名表",
            )
        
        # 检查是否已有待处理的邀请
        existing_invitation = TeamInvitation.objects.filter(
            inviter=user,
            invitee=target_user,
            status='pending'
        ).first()
        
        if existing_invitation:
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="您已经向该用户发送过邀请，请等待对方确认",
            )
        
        # 检查对方是否已向自己发送邀请（双向邀请，直接组队）
        reverse_invitation = TeamInvitation.objects.filter(
            inviter=target_user,
            invitee=user,
            status='pending'
        ).first()
        
        if reverse_invitation:
            # 双方都发送了邀请，直接组队
            from teams.models import Team
            from django.db import transaction
            
            with transaction.atomic():
                team = Team.objects.create(name="")  # 队名由用户自己设置
                
                user.is_match = True
                user.team = team
                user.save()
                
                target_user.is_match = True
                target_user.team = team
                target_user.save()
                
                # 记录匹配关系
                user.people.add(target_user)
                target_user.people.add(user)
                
                # 更新邀请状态
                reverse_invitation.status = 'accepted'
                reverse_invitation.save()
            
            return Response({
                "code": "00000",
                "msg": "组队成功！",
                "data": {
                    "teammate": UserSerializer(target_user).data,
                    "team": TeamInfoSerializer(team).data,
                }
            })
        
        
        # 删除已处理的旧邀请（避免 get_or_create 找到旧记录）
        TeamInvitation.objects.filter(
            inviter=user,
            invitee=target_user,
            status__in=['accepted', 'rejected']
        ).delete()
        
        # 创建邀请（不直接组队）
        invitation, created = TeamInvitation.objects.get_or_create(
            inviter=user,
            invitee=target_user,
            defaults={'status': 'pending'}
        )
        
        if not created:
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="邀请已存在",
            )
        
        return Response({
            "code": "00000",
            "msg": "邀请已发送，等待对方确认",
            "data": {
                "invitationId": invitation.id,
                "invitee": UserSerializer(target_user).data,
            }
        })

    @action(methods=["post"], detail=False, url_path="confirm")
    def confirm_match(self, request):
        """确认匹配并组队（用于同意邀请）"""
        user = request.user
        invitation_id = request.data.get('invitationId') or request.data.get('invitation_id')
        target_user_id = request.data.get('userId') or request.data.get('user_id')
        accept = request.data.get('accept', True)  # 默认同意
        
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
                "code": "00000",
                "msg": "您已经匹配成功",
                "data": {
                    "teammates": UserSerializer(teammates, many=True).data,
                    "team": TeamInfoSerializer(user.team).data if user.team else None,
                }
            })
        
        # 优先通过邀请ID查找邀请
        invitation = None
        if invitation_id:
            try:
                invitation = TeamInvitation.objects.get(
                    id=invitation_id,
                    invitee=user,
                    status='pending'
                )
            except TeamInvitation.DoesNotExist:
                raise ApiException(
                    ResponseType.ResourceNotFound,
                    msg="邀请不存在或已处理",
                )
            target_user = invitation.inviter
        elif target_user_id:
            # 如果没有邀请ID，通过用户ID查找待处理的邀请
            try:
                invitation = TeamInvitation.objects.get(
                    inviter_id=target_user_id,
                    invitee=user,
                    status='pending'
                )
            except TeamInvitation.DoesNotExist:
                # 如果没有邀请，直接通过用户ID组队（兼容旧逻辑）
                try:
                    target_user = User.objects.get(id=target_user_id)
                except User.DoesNotExist:
                    raise ApiException(
                        ResponseType.ResourceNotFound,
                        msg="未找到目标用户",
                    )
            else:
                target_user = invitation.inviter
        else:
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="请提供邀请ID或用户ID",
            )
        
        if not accept:
            # 拒绝邀请
            if invitation:
                invitation.status = 'rejected'
                invitation.save()
            
            return Response({
                "code": "00000",
                "msg": "已拒绝邀请",
                "data": {}
            })
        
        # 同意邀请，执行组队
        if not invitation:
            # 如果没有邀请记录，直接组队（兼容旧逻辑）
            if target_user.is_match:
                raise ApiException(
                    ResponseType.ParamValidationFailed,
                    msg="该用户已匹配",
                )
            
            from django.db import transaction
            with transaction.atomic():
                team = Team.objects.create(name="")  # 队名由用户自己设置
                
                user.team = team
                user.is_match = True
                target_user.team = team
                target_user.is_match = True
                
                user.save()
                target_user.save()
                
                user.people.add(target_user)
                target_user.people.add(user)
        else:
            # 通过邀请组队
            if invitation.inviter.is_match:
                # 邀请方已匹配，拒绝邀请
                invitation.status = 'rejected'
                invitation.save()
                raise ApiException(
                    ResponseType.ParamValidationFailed,
                    msg="邀请方已匹配，无法组队",
                )
            
            from django.db import transaction
            with transaction.atomic():
                team = Team.objects.create(name="")  # 队名由用户自己设置
                
                user.team = team
                user.is_match = True
                invitation.inviter.team = team
                invitation.inviter.is_match = True
                
                user.save()
                invitation.inviter.save()
                
                user.people.add(invitation.inviter)
                invitation.inviter.people.add(user)
                
                # 更新邀请状态
                invitation.status = 'accepted'
                invitation.save()
            
            target_user = invitation.inviter
        
        return Response({
            "code": "00000",
            "msg": "组队成功！",
            "data": {
                "teammate": UserSerializer(target_user).data,
                "team": TeamInfoSerializer(team).data,
            }
        })

    @action(methods=["post"], detail=False, url_path="reject")
    def reject_match(self, request):
        """拒绝匹配，解散队伍并重新进入匹配池"""
        user = request.user
        
        # 检查是否已匹配
        if not user.is_match or not user.team:
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="您还没有匹配，无法拒绝",
            )
        
        team = user.team
        
        # 获取队友
        teammates = User.objects.filter(team=team).exclude(id=user.id)
        
        # 解散队伍（事务内）
        from django.db import transaction
        with transaction.atomic():
            # 重置所有成员的状态
            members = User.objects.filter(team=team)
            members.update(is_match=False, team=None)
            
            # 删除队伍
            team.delete()
            
            # 将队友加入people关系，避免重复匹配
            for teammate in teammates:
                user.people.add(teammate)
                teammate.people.add(user)
        
        return Response({
            "code": "00000",
            "msg": "已拒绝匹配，您已重新进入匹配池",
            "data": {}
        })

    @action(methods=["get"], detail=False, url_path="invitation")
    def get_invitation(self, request):
        """获取待处理的邀请"""
        import logging
        logger = logging.getLogger(__name__)
        
        user = request.user
        logger.info(f"用户 {user.id} ({user.username}) 请求获取邀请")
        
        # 查找待处理的邀请
        invitation = TeamInvitation.objects.filter(
            invitee=user,
            status='pending'
        ).select_related('inviter', 'inviter__academy').first()
        
        if not invitation:
            logger.info(f"用户 {user.id} 没有待处理的邀请")
            return Response({
                "code": "00000",
                "msg": "",
                "data": {
                    "hasInvitation": False,
                    "invitation": None
                }
            })
        
        logger.info(f"用户 {user.id} 找到邀请 ID={invitation.id}, 邀请方={invitation.inviter.username}")
        
        # 获取邀请方的报名表信息
        inviter_application = Application.objects.filter(user=invitation.inviter).first()
        
        inviter_data = UserSerializer(invitation.inviter).data
        if inviter_application:
            inviter_data['majorCategory'] = invitation.inviter.major_category or ''
            inviter_data['college'] = invitation.inviter.academy.name if invitation.inviter.academy else ''
            inviter_data['bio'] = invitation.inviter.interest or ''
        
        return Response({
            "code": "00000",
            "msg": "",
            "data": {
                "hasInvitation": True,
                "invitation": {
                    "id": invitation.id,
                    "inviter": inviter_data,
                    "createdAt": invitation.created_at.isoformat()
                }
            }
        })

    @action(methods=["get"], detail=False, url_path="list")
    def match_list(self, request):
        """获取匹配列表 - 返回当前匹配状态"""
        user = request.user
        
        if not user.is_match or not user.team:
            return Response({
                "code": "00000",
                "msg": "",
                "data": {
                    "matches": [],
                    "isMatched": False,
                }
            })
        
        teammates = User.objects.filter(team=user.team).exclude(id=user.id)
        return Response({
            "code": "00000",
            "msg": "",
            "data": {
                "matches": UserSerializer(teammates, many=True).data,
                "isMatched": True,
                "team": TeamInfoSerializer(user.team).data,
            }
        })

    @action(methods=["get"], detail=False, url_path="team")
    def get_team_info(self, request):
        """获取当前队伍信息"""
        user = request.user
        
        if not user.team:
            raise ApiException(
                ResponseType.ResourceNotFound,
                msg="您还没有加入队伍",
            )
        
        serializer = TeamInfoSerializer(user.team)
        return Response({
            "code": "00000",
            "msg": "",
            "data": serializer.data
        })

    @action(methods=["post"], detail=False, url_path="teamName")
    def set_team_name(self, request):
        """设置队伍名称（只有一次机会，不可二次更改）"""
        user = request.user
        team_name = request.data.get('teamName')
        
        if not user.team:
            raise ApiException(
                ResponseType.ResourceNotFound,
                msg="您还没有加入队伍",
            )
        
        # 检查队名是否已设置，如果已设置则不允许再次修改
        # 但如果队名是系统自动生成的默认格式（"{username}和{username}的队伍"），则允许修改一次
        current_name = user.team.name.strip() if user.team.name else ""
        
        if current_name:
            # 检查是否是系统自动生成的默认队名格式
            # 匹配格式：任意字符+和+任意字符+的队伍
            is_auto_generated = re.match(r'^.+(和|与).+的队伍$', current_name)
            
            if not is_auto_generated:
                # 不是自动生成的格式，说明用户已经设置过，不允许再次修改
                raise ApiException(
                    ResponseType.PermissionDenied,
                    msg="队名只能设置一次，不可二次更改",
                )
            # 如果是自动生成的格式，允许修改一次
        
        if not team_name or not team_name.strip():
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="队伍名称不能为空",
            )
        
        user.team.name = team_name.strip()
        user.team.save()
        
        serializer = TeamInfoSerializer(user.team)
        return Response({
            "code": "00000",
            "msg": "队伍名称设置成功",
            "data": serializer.data
        })

    @action(methods=["post"], detail=False, url_path="disband")
    def disband_team(self, request):
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
            "code": "00000",
            "msg": "队伍已解散",
            "data": {}
        })

    @action(methods=["post"], detail=False, url_path="exchange")
    def request_exchange(self, request):
        """申请换队友"""
        user = request.user
        
        if not user.team:
            raise ApiException(
                ResponseType.ResourceNotFound,
                msg="您还没有加入队伍",
            )
        
        # 获取队友
        teammates = User.objects.filter(team=user.team).exclude(id=user.id)
        if not teammates.exists():
            raise ApiException(
                ResponseType.ResourceNotFound,
                msg="队伍中没有队友",
            )
        
        teammate = teammates.first()
        
        # 检查是否已有待处理的申请
        existing_request = TeamExchangeRequest.objects.filter(
            requester=user,
            teammate=teammate,
            status='pending'
        ).first()
        
        if existing_request:
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="您已发送换队友申请，等待对方回应",
            )
        
        # 删除已处理的旧申请（避免 unique_together 约束冲突）
        TeamExchangeRequest.objects.filter(
            requester=user,
            teammate=teammate,
            status__in=['accepted', 'rejected']
        ).delete()
        
        # 创建换队友申请
        exchange_request = TeamExchangeRequest.objects.create(
            requester=user,
            teammate=teammate,
            status='pending'
        )
        
        return Response({
            "code": "00000",
            "msg": "换队友申请已发送",
            "data": {
                "requestId": exchange_request.id
            }
        })
    
    @action(methods=["get"], detail=False, url_path="exchange")
    def get_exchange_request(self, request):
        """获取待处理的换队友申请"""
        user = request.user
        
        if not user.team:
            return Response({
                "code": "00000",
                "msg": "",
                "data": {
                    "hasRequest": False,
                    "request": None
                }
            })
        
        # 查找是否有队友发起的换队友申请
        teammates = User.objects.filter(team=user.team).exclude(id=user.id)
        if not teammates.exists():
            return Response({
                "code": "00000",
                "msg": "",
                "data": {
                    "hasRequest": False,
                    "request": None
                }
            })
        
        teammate = teammates.first()
        
        # 查找待处理的申请
        exchange_request = TeamExchangeRequest.objects.filter(
            requester=teammate,
            teammate=user,
            status='pending'
        ).select_related('requester').first()
        
        if not exchange_request:
            return Response({
                "code": "00000",
                "msg": "",
                "data": {
                    "hasRequest": False,
                    "request": None
                }
            })
        
        requester_data = UserSerializer(exchange_request.requester).data
        
        return Response({
            "code": "00000",
            "msg": "",
            "data": {
                "hasRequest": True,
                "request": {
                    "id": exchange_request.id,
                    "requester": requester_data,
                    "createdAt": exchange_request.created_at.isoformat()
                }
            }
        })
    
    @action(methods=["post"], detail=False, url_path="exchange/respond")
    def respond_exchange(self, request):
        """响应换队友申请"""
        user = request.user
        request_id = request.data.get('requestId')
        accept = request.data.get('accept', False)
        
        if not request_id:
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="缺少申请ID",
            )
        
        if not user.team:
            raise ApiException(
                ResponseType.ResourceNotFound,
                msg="您还没有加入队伍",
            )
        
        # 查找申请
        exchange_request = TeamExchangeRequest.objects.filter(
            id=request_id,
            teammate=user,
            status='pending'
        ).first()
        
        if not exchange_request:
            raise ApiException(
                ResponseType.ResourceNotFound,
                msg="申请不存在或已处理",
            )
        
        # 更新申请状态
        exchange_request.status = 'accepted' if accept else 'rejected'
        exchange_request.save()
        
        if accept:
            # 同意换队友，解散队伍
            team = user.team
            members = User.objects.filter(team=team)
            members.update(is_match=False, team=None)
            team.delete()
            
            return Response({
                "code": "00000",
                "msg": "已同意换队友申请，队伍已解散",
                "data": {}
            })
        else:
            # 拒绝换队友，保持队伍
            return Response({
                "code": "00000",
                "msg": "已拒绝换队友申请",
                "data": {}
            })

    @action(methods=["get"], detail=False, url_path="checkDisband")
    def check_disband_permission(self, request):
        """检查是否可以拆队（是否已用过拆队机会）"""
        # 暂时返回可以拆队
        return Response({
            "code": "00000",
            "msg": "",
            "data": {
                "canDisband": True,
                "hasUsed": False,
            }
        })

    @action(methods=["post", "get"], detail=False, url_path="expectation")
    def match_expectation(self, request):
        """保存/获取匹配期望"""
        user = request.user
        
        # 获取或创建报名表
        application, created = Application.objects.get_or_create(
            user=user,
            defaults={'phone': '', 'qq': ''}
        )
        
        if request.method == 'POST':
            # 保存匹配期望
            serializer = MatchExpectationSerializer(data=request.data)
            if not serializer.is_valid():
                raise ApiException(
                    ResponseType.ParamValidationFailed,
                    msg="数据验证失败",
                    detail=str(serializer.errors),
                )
            
            validated_data = serializer.validated_data
            
            # 更新匹配期望字段
            if 'gender' in validated_data:
                gender_value = validated_data['gender']
                # 转换前端格式到数据库格式
                if gender_value == '男' or gender_value == 'male':
                    application.gender_choice = '男'
                elif gender_value == '女' or gender_value == 'female':
                    application.gender_choice = '女'
                else:
                    application.gender_choice = '无'
            
            if 'degree' in validated_data:
                application.degree_choice = validated_data['degree'] or ''
            
            if 'majorCategory' in validated_data:
                application.major_category_choice = validated_data['majorCategory'] or ''
            
            if 'college' in validated_data:
                college_value = validated_data['college']
                if isinstance(college_value, Academy):
                    application.college_choice = college_value
                elif college_value:
                    try:
                        academy = Academy.objects.get(name=college_value)
                        application.college_choice = academy
                    except Academy.DoesNotExist:
                        application.college_choice = None
                else:
                    application.college_choice = None
            
            application.save()
            
            return Response({
                "code": "00000",
                "msg": "匹配期望已保存",
                "data": {
                    "gender": application.gender_choice,
                    "degree": application.degree_choice,
                    "majorCategory": application.major_category_choice,
                    "college": application.college_choice.name if application.college_choice else None,
                }
            })
        else:
            # 获取匹配期望
            return Response({
                "code": "00000",
                "msg": "",
                "data": {
                    "gender": application.gender_choice or None,
                    "degree": application.degree_choice or None,
                    "majorCategory": application.major_category_choice or None,
                    "college": application.college_choice.name if application.college_choice else None,
                }
            })

