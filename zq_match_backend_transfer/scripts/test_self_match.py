"""
自助匹配接口最小验证
- 创建两个报名用户（互选院系、性别不冲突）
- 触发 self-match，期望成功组队
- 再次触发 self-match，返回已匹配
"""
import os
import sys
import django

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
APPS_DIR = os.path.join(ROOT_DIR, 'server', 'apps')
if APPS_DIR not in sys.path:
    sys.path.insert(0, APPS_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from academies.models import Academy  # type: ignore[reportMissingImports]
from applications.models import Application  # type: ignore[reportMissingImports]
from django.conf import settings

# 允许测试主机
settings.ALLOWED_HOSTS = list(set(getattr(settings, 'ALLOWED_HOSTS', [])) | {"testserver", "localhost", "127.0.0.1"})

User = get_user_model()


def ensure_user(username: str, email: str):
    u, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'grade': 2024,
            'gender': 1,
        }
    )
    if created:
        u.set_password('test123456')
        u.save()
    return u


def main():
    # 基础数据
    a1, _ = Academy.objects.get_or_create(name='学院A')
    a2, _ = Academy.objects.get_or_create(name='学院B')

    u1 = ensure_user('self_match_u1', 'u1@example.com')
    u2 = ensure_user('self_match_u2', 'u2@example.com')

    # 报名表（互选）
    app1, _ = Application.objects.get_or_create(user=u1, defaults={
        'my_academy': a1,
        'my_gender': '男',
        'gender_choice': '无',
        'phone': '13800138000',
        'qq': '10001',
    })
    app1.academy_choice.set([a2])

    app2, _ = Application.objects.get_or_create(user=u2, defaults={
        'my_academy': a2,
        'my_gender': '男',
        'gender_choice': '无',
        'phone': '13800138002',
        'qq': '10002',
    })
    app2.academy_choice.set([a1])

    client = APIClient()
    # 登录 u1（使用 DRF JWT 或 Session 均可，这里直接强制认证）
    client.force_authenticate(user=u1)

    # 触发自助匹配
    resp = client.post('/applications/self-match/')
    print('第一次匹配:', resp.status_code, resp.data)

    # 再次触发
    resp2 = client.post('/applications/self-match/')
    print('第二次匹配:', resp2.status_code, resp2.data)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
