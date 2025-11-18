from django.db import models
from django.db.models import SET_NULL

from tasks.models import Task
from teams.models import Team


class Post(models.Model):
    """
    上传打卡表
    """

    title = models.CharField(max_length=50, blank=True, verbose_name="打卡标题")
    description = models.TextField(blank=True, verbose_name="打卡内容描述")
    photo = models.ImageField(upload_to=r"post\photo", verbose_name="打卡配图")

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="对应的任务",
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="所属队伍",
    )

    class Meta:
        app_label = "posts"
        db_table = "zq_match_post"
        verbose_name = "打卡"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title
