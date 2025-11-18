from datetime import datetime
from django.db import transaction
from django.utils import timezone

from academies.models import Academy
from applications.models import Application, MatchAttempt
from teams.models import Team
from users.models import User


DAILY_ATTEMPT_LIMIT = 3


def _today_range():
    now = timezone.now()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start.replace(hour=23, minute=59, second=59, microsecond=999999)
    return start, end


def _get_today_attempts(user: User) -> int:
    start, end = _today_range()
    return MatchAttempt.objects.filter(user=user, created_at__range=(start, end)).count()


def _score_pair(me: Application, other: Application) -> int:
    """
    加权评分：按图片机制近似实现（院系互选、性别偏好、同院系、年级差、未匹配）
    返回分数越高越优
    """
    score = 0

    # 互选院系
    my_like_ids = set(me.academy_choice.values_list('id', flat=True))
    other_like_ids = set(other.academy_choice.values_list('id', flat=True))
    if me.my_academy_id in other_like_ids and other.my_academy_id in my_like_ids:
        score += 40
    elif me.my_academy_id in other_like_ids or other.my_academy_id in my_like_ids:
        score += 20

    # 性别偏好（如果有要求）
    if me.gender_choice and me.gender_choice != '无':
        if other.my_gender == me.gender_choice:
            score += 15
        else:
            return -1  # 不满足硬性条件
    if other.gender_choice and other.gender_choice != '无':
        if me.my_gender == other.gender_choice:
            score += 15
        else:
            return -1

    # 同院系加分
    if me.my_academy_id and other.my_academy_id and me.my_academy_id == other.my_academy_id:
        score += 10

    # 年级差距加分（越近越好）
    try:
        me_grade = me.user.grade or 0
        other_grade = other.user.grade or 0
        diff = abs(int(me_grade) - int(other_grade))
        if diff == 0:
            score += 10
        elif diff == 1:
            score += 6
        elif diff == 2:
            score += 3
    except Exception:
        pass

    return score


@transaction.atomic
def match(user_id: int, *, enforce_limit: bool = True):
    """
    自助匹配：返回匹配到的用户（并直接组队）或 None
    规则：
    - 每日最多尝试3次（可配置），超过限制直接返回 None
    - 过滤：未匹配、未曾匹配过、不是自己
    - 评分：互选院系>单向院系>性别偏好>同院系>年级差
    - 选取最高分，分数相同按报名表创建顺序
    成功则创建队伍、双方 is_match=True，写入 people 关系；记录尝试日志
    """
    try:
        user = User.objects.select_related().get(id=user_id)
    except User.DoesNotExist:
        return None

    # 限制：已在队伍或已匹配直接返回当前队友
    if user.is_match and user.team_id:
        return User.objects.filter(team_id=user.team_id).exclude(id=user.id).first()

    me = Application.objects.select_related('user', 'my_academy').prefetch_related('academy_choice').filter(user=user).first()
    if me is None or me.my_academy_id is None:
        return None

    # 每日尝试限制
    if enforce_limit and _get_today_attempts(user) >= DAILY_ATTEMPT_LIMIT:
        return None

    ex_people_ids = list(user.people.values_list('id', flat=True))

    # 候选集合：
    candidates = (
        Application.objects.select_related('user', 'my_academy')
        .prefetch_related('academy_choice')
        .filter(user__is_match=False)
        .exclude(user_id__in=ex_people_ids + [user_id])
    )

    # 计算得分并挑选最佳
    best = None
    best_score = -1
    for other in candidates:
        s = _score_pair(me, other)
        if s > best_score:
            best_score = s
            best = other

    # 记录一次尝试（先记失败，成功时再更新）
    attempt = MatchAttempt.objects.create(user=user, success=False)

    if not best or best_score < 0:
        return None

    match_user = best.user

    # 组队（事务内）
    team = Team.objects.create(name=f"{user.username}和{match_user.username}的队伍")

    user.team = team
    user.is_match = True
    match_user.team = team
    match_user.is_match = True

    # 双向记录历史
    user.save()
    match_user.save()
    user.people.add(match_user)
    match_user.people.add(user)

    attempt.success = True
    attempt.save(update_fields=['success'])

    return match_user
