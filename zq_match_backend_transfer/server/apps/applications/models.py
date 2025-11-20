from django.db import models

from academies.models import Academy


class Application(models.Model):
    """
    报名表模型
    """

    # 关联外键
    user = models.ForeignKey(
        'users.User',
        related_name='application_form',
        on_delete=models.CASCADE,
        verbose_name='用户'
    )

    my_academy = models.ForeignKey(
        Academy,
        on_delete=models.CASCADE,
        null=True,
        verbose_name="我的专业",
    )
    academy_choice = models.ManyToManyField(
        Academy,
        related_name="applications",
        verbose_name="愿意交换的专业"
    )

    my_gender = models.CharField(
        max_length=3,
        verbose_name='我的性别',
        default='无',
    )
    gender_choice = models.CharField(
        max_length=3,
        verbose_name='选择同伴性别',
        default='无'
    )
    
    # 匹配期望字段
    degree_choice = models.CharField(
        max_length=20,
        verbose_name='期望同伴学历',
        default='',
        blank=True,
        help_text='本科/研究生'
    )
    major_category_choice = models.CharField(
        max_length=50,
        verbose_name='期望同伴大类',
        default='',
        blank=True
    )
    college_choice = models.ForeignKey(
        Academy,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='college_choice_applications',
        verbose_name='期望同伴学院'
    )

    phone = models.CharField(max_length=11, verbose_name='手机号码')
    qq = models.CharField(max_length=11, verbose_name='qq号码')

    def __str__(self):
        return '用户: {}'.format(self.user)

    class Meta:
        app_label = 'applications'
        db_table = "zq_match_applications"
        verbose_name = '报名表'
        verbose_name_plural = '报名表'


class MatchAttempt(models.Model):
    """
    自助匹配尝试记录
    用于限制每日匹配次数、统计成功与否
    """
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='match_attempts',
        verbose_name='用户'
    )
    success = models.BooleanField(default=False, verbose_name='是否成功')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        app_label = 'applications'
        db_table = 'zq_match_attempt'
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]
        verbose_name = '匹配尝试'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user_id} - {'成功' if self.success else '失败'} @ {self.created_at}"


class TeamInvitation(models.Model):
    """
    组队邀请模型
    用于存储待确认的组队邀请
    """
    inviter = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='sent_invitations',
        verbose_name='邀请方'
    )
    invitee = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='received_invitations',
        verbose_name='被邀请方'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', '待确认'),
            ('accepted', '已同意'),
            ('rejected', '已拒绝'),
        ],
        default='pending',
        verbose_name='邀请状态'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        app_label = 'applications'
        db_table = 'zq_match_team_invitation'
        unique_together = [('inviter', 'invitee')]
        indexes = [
            models.Index(fields=['invitee', 'status']),
            models.Index(fields=['inviter', 'status']),
        ]
        verbose_name = '组队邀请'
        verbose_name_plural = '组队邀请'

    def __str__(self):
        return f"{self.inviter.username} -> {self.invitee.username} ({self.status})"


class TeamExchangeRequest(models.Model):
    """
    换队友申请模型
    用于存储待确认的换队友申请
    """
    requester = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='sent_exchange_requests',
        verbose_name='申请方'
    )
    teammate = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='received_exchange_requests',
        verbose_name='队友'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', '待确认'),
            ('accepted', '已同意'),
            ('rejected', '已拒绝'),
        ],
        default='pending',
        verbose_name='申请状态'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        app_label = 'applications'
        db_table = 'zq_match_team_exchange_request'
        unique_together = [('requester', 'teammate')]
        indexes = [
            models.Index(fields=['teammate', 'status']),
            models.Index(fields=['requester', 'status']),
        ]
        verbose_name = '换队友申请'
        verbose_name_plural = '换队友申请'

    def __str__(self):
        return f"{self.requester.username} -> {self.teammate.username} ({self.status})"
