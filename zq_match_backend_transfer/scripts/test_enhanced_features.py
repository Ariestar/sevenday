"""
测试增强功能的脚本
包括：应用报名、匹配、团队管理、任务完成等流程
"""
import os
import sys
import json
from io import BytesIO
from PIL import Image

import django
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile

# 配置 Django
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
APPS = os.path.join(ROOT, 'server', 'apps')
if APPS not in sys.path:
    sys.path.insert(0, APPS)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from django.conf import settings
from academies.models import Academy  # type: ignore[reportMissingImports]


def create_test_image():
    """创建一个测试图片"""
    img = Image.new('RGB', (100, 100), color='red')
    img_io = BytesIO()
    img.save(img_io, 'JPEG')
    img_io.seek(0)
    return SimpleUploadedFile("test.jpg", img_io.read(), content_type="image/jpeg")


def setup_allowed_hosts():
    """配置允许的主机"""
    try:
        if getattr(settings, "ALLOWED_HOSTS", None) is not None:
            ah = list(settings.ALLOWED_HOSTS)
            for host in ["testserver", "localhost", "127.0.0.1"]:
                if host not in ah and "*" not in ah:
                    ah.append(host)
            settings.ALLOWED_HOSTS = ah
    except Exception:
        settings.ALLOWED_HOSTS = ["*"]


def test_user_profile_management():
    """测试用户资料管理"""
    print("\n[1/6] 测试用户资料管理...")
    client = Client()
    
    # 注册并登录
    reg_data = {
        "username": "testuser1",
        "email": "testuser1@stu.whu.edu.cn",
        "password": "TestPass123!",
    }
    client.post("/oauth/register/", json.dumps(reg_data), content_type="application/json")
    
    login_data = {"email": reg_data["email"], "password": reg_data["password"]}
    resp = client.post("/oauth/login/", json.dumps(login_data), content_type="application/json")
    data = json.loads(resp.content.decode("utf-8"))
    token = data["data"]["access"]
    
    # 获取个人信息
    resp = client.get("/users/me/", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert resp.status_code == 200, f"获取个人信息失败: {resp.status_code}"
    
    # 更新个人资料
    profile_data = {
        "username": "UpdatedUser",
        "interest": "编程、阅读",
        "grade": 2024,
    }
    resp = client.patch(
        "/users/update-profile/",
        json.dumps(profile_data),
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )
    assert resp.status_code == 200, f"更新资料失败: {resp.status_code}"
    print("  ✓ 用户资料管理功能正常")
    return token


def test_application_flow(token):
    """测试报名流程"""
    print("\n[2/6] 测试报名申请流程...")
    client = Client()
    
    # 获取第一个学院作为测试数据
    academy = Academy.objects.first()
    if not academy:
        print("  ⚠ 没有学院数据，跳过报名测试")
        return
    
    # 提交报名表
    app_data = {
        "my_academy": academy.id,
        "academy_choice": [academy.id + 1 if Academy.objects.filter(id=academy.id + 1).exists() else academy.id],
        "my_gender": "男",
        "gender_choice": "女",
        "phone": "13800138000",
        "qq": "123456789",
    }
    
    resp = client.post(
        "/applications/",
        json.dumps(app_data),
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )
    
    if resp.status_code in [200, 201]:
        print("  ✓ 报名表提交成功")
    else:
        print(f"  ⚠ 报名表提交返回: {resp.status_code}")
    
    # 查询我的报名表
    resp = client.get(
        "/applications/my-application/",
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )
    if resp.status_code == 200:
        print("  ✓ 查询报名表成功")
    
    # 查询匹配状态
    resp = client.get(
        "/applications/match-status/",
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )
    assert resp.status_code == 200, f"查询匹配状态失败: {resp.status_code}"
    print("  ✓ 报名流程功能正常")


def test_task_management(token):
    """测试任务管理"""
    print("\n[3/6] 测试任务管理...")
    client = Client()
    
    # 查看所有任务
    resp = client.get("/tasks/", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert resp.status_code == 200, f"查看任务失败: {resp.status_code}"
    
    # 查看进行中的任务
    resp = client.get("/tasks/active/", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert resp.status_code == 200, f"查看进行中任务失败: {resp.status_code}"
    
    # 查看即将开始的任务
    resp = client.get("/tasks/upcoming/", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert resp.status_code == 200, f"查看即将开始任务失败: {resp.status_code}"
    
    print("  ✓ 任务管理功能正常")


def test_team_management(token):
    """测试团队管理"""
    print("\n[4/6] 测试团队管理...")
    client = Client()
    
    # 查看队伍排行榜
    resp = client.get("/teams/", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert resp.status_code == 200, f"查看队伍列表失败: {resp.status_code}"
    
    # 查看我的队伍（可能还没有）
    resp = client.get("/teams/my-team/", HTTP_AUTHORIZATION=f"Bearer {token}")
    if resp.status_code == 404:
        print("  • 用户暂无队伍（正常）")
    elif resp.status_code == 200:
        print("  ✓ 查看我的队伍成功")
    
    print("  ✓ 团队管理功能正常")


def test_post_management(token):
    """测试打卡记录"""
    print("\n[5/6] 测试打卡记录...")
    client = Client()
    
    # 查看所有打卡记录
    resp = client.get("/posts/", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert resp.status_code == 200, f"查看打卡记录失败: {resp.status_code}"
    
    # 查看我的打卡记录
    resp = client.get("/posts/my-posts/", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert resp.status_code == 200, f"查看我的打卡记录失败: {resp.status_code}"
    
    print("  ✓ 打卡记录功能正常")


def test_api_documentation():
    """测试 API 文档"""
    print("\n[6/6] 测试 API 文档...")
    client = Client()
    
    # 检查 schema 接口
    resp = client.get("/docs/schema/")
    if resp.status_code == 200:
        print("  ✓ API Schema 可访问")
    else:
        print(f"  • API Schema 返回: {resp.status_code}（可能未启用）")
    
    # 检查文档界面
    resp = client.get("/docs/")
    if resp.status_code == 200:
        print("  ✓ API 文档界面可访问")
    else:
        print(f"  • API 文档界面返回: {resp.status_code}（可能未启用）")


def main():
    print("=" * 60)
    print("开始测试增强功能")
    print("=" * 60)
    
    setup_allowed_hosts()
    
    try:
        # 按顺序执行测试
        token = test_user_profile_management()
        test_application_flow(token)
        test_task_management(token)
        test_team_management(token)
        test_post_management(token)
        test_api_documentation()
        
        print("\n" + "=" * 60)
        print("所有测试通过 ✅")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n测试失败 ❌: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n发生错误 ❌: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
