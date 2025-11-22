"""
邮件配置
"""
from server.settings.util import config

# 邮件后端配置
EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend"
)

# SMTP 服务器配置
EMAIL_HOST = config("EMAIL_HOST", "smtp.whu.edu.cn")  # 武大邮箱服务器
EMAIL_PORT = config("EMAIL_PORT", 587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", True, cast=bool)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", False, cast=bool)

# 发件人配置
EMAIL_HOST_USER = config("EMAIL_HOST_USER", "")  # 发件邮箱
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", "")  # 发件邮箱密码或授权码
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

# SMTP连接超时设置（秒）
EMAIL_TIMEOUT = config("EMAIL_TIMEOUT", 30, cast=int)  # 30秒超时

# 开发环境：如果未配置邮件，使用控制台后端
if not EMAIL_HOST_USER:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

