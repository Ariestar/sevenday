import os
import sys
import json

import django
from django.test import Client
from django.conf import settings


# Ensure project root on sys.path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def run():
    # 允许 testserver 作为主机名
    try:
        if getattr(settings, "ALLOWED_HOSTS", None) is not None:
            # 将其转换为列表并追加 testserver
            ah = list(settings.ALLOWED_HOSTS)
            for host in ["testserver", "localhost", "127.0.0.1"]:
                if host not in ah and "*" not in ah:
                    ah.append(host)
            settings.ALLOWED_HOSTS = ah
    except Exception:
        # 最差退路：放开所有（仅用于本地脚本）
        settings.ALLOWED_HOSTS = ["*"]

    client = Client()

    print("[1/4] Admin 登录...")
    # Django admin uses username/password
    admin_username = os.environ.get("LOCAL_ADMIN_USERNAME", "admin")
    admin_password = os.environ.get("LOCAL_ADMIN_PASSWORD", "Testpass123!")

    resp = client.post("/admin/login/?next=/admin/", {
        "username": admin_username,
        "password": admin_password,
    }, follow=False)
    # Expect redirect to /admin/
    assert_true(resp.status_code in (302, 301), f"Admin 登录期望 30x，实际 {resp.status_code}")
    assert_true("sessionid" in client.cookies, "Admin 登录后未设置 sessionid cookie")
    # Authenticated access to /admin/
    resp = client.get("/admin/")
    assert_true(resp.status_code == 200, f"访问 /admin/ 期望 200，实际 {resp.status_code}")
    print("  ✓ Admin 登录成功")

    print("[2/4] 注册一个用于邮箱登录的测试用户...")
    # Use a valid WHU email domain
    reg_payload = {
        "username": "apiuser",
        "email": "apiuser@stu.whu.edu.cn",
        "password": "ApiPass123!",
    }
    resp = client.post(
        "/oauth/register/",
        data=json.dumps(reg_payload),
        content_type="application/json",
    )
    assert_true(resp.status_code in (201, 400), f"注册返回 {resp.status_code}")
    if resp.status_code == 400:
        #可能已注册，继续
        print("  • 用户可能已存在，跳过创建")
    else:
        print("  ✓ 注册成功")

    print("[3/4] 邮箱登录获取 JWT...")
    login_payload = {
        "email": reg_payload["email"],
        "password": reg_payload["password"],
    }
    resp = client.post(
        "/oauth/login/",
        data=json.dumps(login_payload),
        content_type="application/json",
    )
    assert_true(resp.status_code == 200, f"邮箱登录失败: {resp.status_code} {getattr(resp, 'content', b'')[:256]}")
    raw = resp.content.decode("utf-8")
    try:
        data = json.loads(raw)
    except Exception:
        data = {}
        print("  • 警告：响应非 JSON:", raw[:256])
    payload = data.get("data", data)
    access = payload.get("access")
    refresh = payload.get("refresh")
    if not (access and refresh):
        print("  • 登录响应:", data)
    assert_true(access and refresh, "未获取到 access/refresh token")
    print("  ✓ 邮箱登录成功，已获取 JWT")

    print("[4/4] 使用 JWT 访问受保护接口（QQ 绑定）...")
    # Try bind qq with a dummy number
    resp = client.post(
        "/oauth/bind/qq/",
        data=json.dumps({"qq": "123456789"}),
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {access}",
    )
    assert_true(resp.status_code in (200, 400), f"QQ 绑定返回 {resp.status_code}")
    if resp.status_code == 200:
        print("  ✓ QQ 绑定成功")
    else:
        print("  • QQ 绑定未成功（可能已绑定/校验失败），但 JWT 鉴权通路正常")

    print("\nSmoke test PASS ✅")


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print("Smoke test FAIL ❌:\n", str(e))
        sys.exit(1)
