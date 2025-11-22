from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import SET_NULL
from zq_django_util.utils.user.models import AbstractUser

from academies.models import Academy
# from applications.models import Application  # 避免循环导入，使用字符串引用
from server.utils.choices import GenderType
from teams.models import Team

import uuid


class User(AbstractUser):
    """
    基本用户表
    """
    # 身份信息
    username = models.CharField(
        "用户名",
        max_length=150,
        unique=True,
        validators=[UnicodeUsernameValidator()],
    )
    email = models.EmailField("邮箱", unique=True, blank=True)
    phone = models.CharField(max_length=13, default="", verbose_name="手机")
    qq = models.CharField(max_length=16, unique=True, blank=True, null=True, verbose_name="QQ")
    wechat = models.CharField(max_length=25, default="", verbose_name="wechat")
    school_number = models.CharField(max_length=20, default="", verbose_name="学号")

    # 个性化信息
    avatar = models.ImageField(
        upload_to="avatar",
        default=r"avatar\default.jpg",
        verbose_name="头像"
    )
    gender = models.IntegerField(
        choices=GenderType.choices,
        default=GenderType.UNKNOWN,
        verbose_name="性别",
    )
    academy = models.ForeignKey(
        Academy,
        on_delete=models.CASCADE,
        related_name="academy_users",
        null=True,
        blank=True,
        verbose_name="院系",
    )
    grade = models.IntegerField(default=0, verbose_name="年级")
    interest = models.TextField(max_length=500, default="", verbose_name="爱好")
    major_category = models.CharField(max_length=50, default="", blank=True, verbose_name="专业大类")

    # 报名表 related_name = application_form

    # 是否匹配
    is_match = models.BooleanField(default=False, verbose_name="是否匹配")
    # 队伍
    team = models.ForeignKey(
        Team,
        on_delete=SET_NULL,
        null=True,
        related_name="users",
        verbose_name="队伍",
    )
    # 匹配过的人
    people = models.ManyToManyField(
        "self",
        blank=True,
        verbose_name="以前匹配过的用户们"
    )

    # 权限与认证
    is_authenticated = models.BooleanField("是否激活", default=True)
    is_staff = models.BooleanField("管理员", default=False)
    is_superuser = models.BooleanField("超级用户", default=False)
    password = models.CharField(max_length=64, null=True, verbose_name="密码")
    openid = models.CharField(
        max_length=64,
        unique=True,
        null=True,
        verbose_name="微信openid")
    union_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        null=True,
        blank=True,
        verbose_name="自强union_id"
    )

    # 时间
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return self.username

    class Meta:
        app_label = "users"
        db_table = "zq_match_user"
        verbose_name = "用户"
        verbose_name_plural = verbose_name
