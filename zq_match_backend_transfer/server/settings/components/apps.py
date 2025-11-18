DJANGO_APPS: list[str] = [
    "simpleui",  # admin ui（必须在第一行）
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS: list[str] = [
    "rest_framework",  # DRF
    "corsheaders",  # CORS 跨域
    "rest_framework_simplejwt",  # JWT
    "drf_spectacular",  # api 文档 !!!
    "django_filters",  # 过滤器
    "zq_django_util.utils.oss",  # oss
    "method_override",  # 方法重写 !!!
    "drf_standardized_errors",  # drf错误初步处理
    "django_extensions",  # Django 扩展 !!!
    # "cacheops",  # ORM缓存 !!!
    # "django_celery_results",  # celery兼容支持 !!!
    # "django_celery_beat",  # celery定时任务 !!!
]

LOCAL_APPS: list[str] = [
    # "async_tasks",  # celery异步任务 !!!
    "users",  # 用户
    "oauth",  # 登录
    "applications",  # 报名表
    "academies",  # 学院
    "posts",  # 提交任务单
    "tasks",  # 任务
    "teams",  # 队伍
]

INSTALLED_APPS: list[str] = (
    DJANGO_APPS
    + THIRD_PARTY_APPS
    + LOCAL_APPS
    + ["django_cleanup.apps.CleanupConfig"]  # 清理OSS文件, 需要放在最后
)

MIDDLEWARE: list[str] = [
    "corsheaders.middleware.CorsMiddleware",  # CORS 跨域(最外层)
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "method_override.middleware.MethodOverrideMiddleware",  # 请求方法修改
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "server.urls"

WSGI_APPLICATION = "server.wsgi.application"
ASGI_APPLICATION = "server.asgi.application"
