from django.db import models
from django.db.models import SET_NULL
from django.contrib.contenttypes.fields import GenericRelation

from tasks.models import Task
from teams.models import Team
from users.models import User


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
    
    # 是否发布到广场
    is_published = models.BooleanField(default=False, verbose_name="是否发布到广场")
    
    # 浏览量
    view_count = models.IntegerField(default=0, verbose_name="浏览量")
    
    # 时间字段
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        app_label = "posts"
        db_table = "zq_match_post"
        verbose_name = "打卡"
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.title


class PostLike(models.Model):
    """打卡点赞表"""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="打卡记录"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="post_likes",
        verbose_name="点赞用户"
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="点赞时间")

    class Meta:
        app_label = "posts"
        db_table = "zq_match_post_like"
        verbose_name = "打卡点赞"
        verbose_name_plural = verbose_name
        unique_together = [['post', 'user']]  # 每个用户对每个打卡只能点赞一次

    def __str__(self):
        return f"{self.user.username} 点赞了 {self.post.title}"


class PostComment(models.Model):
    """打卡评论表"""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="打卡记录"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="post_comments",
        verbose_name="评论用户"
    )
    content = models.TextField(max_length=500, verbose_name="评论内容")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="评论时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        app_label = "posts"
        db_table = "zq_match_post_comment"
        verbose_name = "打卡评论"
        verbose_name_plural = verbose_name
        ordering = ['create_time']

    def __str__(self):
        return f"{self.user.username} 评论了 {self.post.title}"
