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
