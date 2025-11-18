from rest_framework.test import APITestCase
from django.urls import reverse

from users.models import User


class EmailLoginTests(APITestCase):
    def setUp(self):
        # 创建一个可登录的测试用户（武大邮箱）
        self.user = User.objects.create(
            username="testuser",
            email="testuser@whu.edu.cn",
            is_authenticated=True,
            is_staff=False,
        )
        # 使用模型的 set_password 方法设置密码
        try:
            self.user.set_password("Testpass123!")
        except Exception:
            # 某些自定义 AbstractUser 可能不实现 set_password，直接赋值并 save
            self.user.password = "Testpass123!"
        self.user.save()

    def test_email_login_success(self):
        """成功登录应返回 access 和 refresh token"""
        url = reverse("email_login")
        data = {"email": "testuser@whu.edu.cn", "password": "Testpass123!"}
        resp = self.client.post(url, data, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)

    def test_email_login_invalid_domain(self):
        """非武大邮箱应返回校验错误"""
        url = reverse("email_login")
        data = {"email": "user@example.com", "password": "whatever"}
        resp = self.client.post(url, data, format="json")
        # 期望非 200（通常为 400）
        self.assertNotEqual(resp.status_code, 200)
