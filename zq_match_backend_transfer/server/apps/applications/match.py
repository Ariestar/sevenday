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
    加权评分：按图片机制近似实现（院系互选、性别偏好、身份匹配、大类匹配、学院匹配、同院系、年级差）
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

    # 身份（学历）匹配
    if me.degree_choice:
        # 根据用户的年级推断学历：1-4年级为本科，5-6年级为研究生
        other_grade = other.user.grade or 0
        other_degree = '本科' if other_grade <= 4 else ('研究生' if other_grade <= 6 else '')
        if other_degree and me.degree_choice == other_degree:
            score += 12
        elif me.degree_choice and other_degree and me.degree_choice != other_degree:
            # 如果明确要求但不符合，可以降低分数但不直接拒绝
            score -= 5
    
    if other.degree_choice:
        me_grade = me.user.grade or 0
        me_degree = '本科' if me_grade <= 4 else ('研究生' if me_grade <= 6 else '')
        if me_degree and other.degree_choice == me_degree:
            score += 12
        elif other.degree_choice and me_degree and other.degree_choice != me_degree:
            score -= 5

    # 大类匹配
    if me.major_category_choice:
        other_major = getattr(other.user, 'major_category', '') or ''
        if other_major and me.major_category_choice == other_major:
            score += 10
        elif me.major_category_choice and other_major and me.major_category_choice != other_major:
            score -= 3
    
    if other.major_category_choice:
        me_major = getattr(me.user, 'major_category', '') or ''
        if me_major and other.major_category_choice == me_major:
            score += 10
        elif other.major_category_choice and me_major and other.major_category_choice != me_major:
            score -= 3

    # 学院匹配（期望学院）
    if me.college_choice_id:
        if other.my_academy_id == me.college_choice_id:
            score += 15
        elif other.my_academy_id:
            # 如果期望学院但不符合，可以降低分数
            score -= 2
    
    if other.college_choice_id:
        if me.my_academy_id == other.college_choice_id:
            score += 15
        elif me.my_academy_id:
            score -= 2

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


def recommend_matches(user_id: int, limit: int = 10):
    """
    推荐匹配对象：返回候选列表（不直接组队）
    规则：
    - 过滤：未匹配、未曾匹配过、不是自己
    - 评分：互选院系>单向院系>性别偏好>同院系>年级差
    - 返回前N个候选，包含匹配分数和用户信息
    """
    try:
        user = User.objects.select_related().get(id=user_id)
    except User.DoesNotExist:
        return []
    
    me = Application.objects.select_related('user', 'my_academy', 'college_choice').prefetch_related('academy_choice').filter(user=user).first()
    if me is None or me.my_academy_id is None:
        return []
    
    ex_people_ids = list(user.people.values_list('id', flat=True))
    
    # 候选集合：
    candidates = (
        Application.objects.select_related('user', 'my_academy')
        .prefetch_related('academy_choice')
        .filter(user__is_match=False)
        .exclude(user_id__in=ex_people_ids + [user_id])
    )
    
    # 计算得分并排序
    scored_candidates = []
    for other in candidates:
        s = _score_pair(me, other)
        if s >= 0:  # 只返回满足基本条件的候选
            scored_candidates.append({
                'application': other,
                'user': other.user,
                'score': s
            })
    
    # 按分数降序排序，分数相同按报名表创建顺序
    scored_candidates.sort(key=lambda x: (-x['score'], x['application'].id))
    
    # 返回前N个
    return scored_candidates[:limit]


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
