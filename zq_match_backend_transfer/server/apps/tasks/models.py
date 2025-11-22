from django.db import models


class Task(models.Model):
    """
    打卡任务模型
    """
    title = models.CharField(max_length=50, blank=True, verbose_name="任务名")
    cover = models.ImageField(upload_to=r"task\cover", verbose_name="封面", blank=True, null=True)
    introduction = models.TextField(blank=True, verbose_name="任务描述")
    score = models.IntegerField(blank=True, default=100, verbose_name="任务分数")

    start_time = models.DateField(verbose_name="开始时间")
    end_time = models.DateField(verbose_name="结束时间")

    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        app_label = "tasks"
        db_table = "zq_match_tasks"
        verbose_name = "打卡任务"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title
