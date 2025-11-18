from django.db import models

from tasks.models import Task


class Team(models.Model):
    """
    队伍
    """

    name = models.CharField(max_length=30, blank=True, verbose_name="队伍名")
    introduction = models.TextField(blank=True, verbose_name="队伍口号")

    score = models.IntegerField(blank=True, default=0, verbose_name="得分")
    task = models.ManyToManyField(
        Task,
        related_name="teams",
        blank=True,
        verbose_name="完成的任务",
    )

    # 队伍中的两个人用user字段查取，由User类中的team字段的related_name指定

    class Meta:
        app_label = "teams"
        db_table = "zq_match_team"
        verbose_name = "队伍"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
