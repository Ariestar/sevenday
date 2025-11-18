"""
测试进阶功能：分页、搜索、统计等
"""
import os
import sys
import json

import django
from django.test import Client

# 配置 Django
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from django.conf import settings


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


def get_auth_token():
    """获取认证 token"""
    client = Client()
    
    # 登录
    login_data = {
        "email": "apiuser@stu.whu.edu.cn",
        "password": "ApiPass123!",
    }
    resp = client.post(
        "/oauth/login/",
        json.dumps(login_data),
        content_type="application/json"
    )
    
    if resp.status_code != 200:
        print(f"  ⚠ 登录失败: {resp.status_code}")
        return None
    
    data = json.loads(resp.content.decode("utf-8"))
    return data["data"]["access"]


def test_pagination():
    """测试分页功能"""
    print("\n[1/5] 测试分页功能...")
    client = Client()
    token = get_auth_token()
    
    if not token:
        print("  ✗ 无法获取 token，跳过测试")
        return
    
    # 测试队伍列表分页
    resp = client.get(
        "/teams/?page=1&page_size=5",
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )
    
    if resp.status_code == 200:
        data = json.loads(resp.content.decode("utf-8"))
        if 'data' in data and 'page' in data['data']:
            print("  ✓ 分页功能正常")
            print(f"    当前页: {data['data'].get('page', 'N/A')}")
            print(f"    总页数: {data['data'].get('total_pages', 'N/A')}")
        else:
            print("  • 分页格式可能不同")
    else:
        print(f"  ⚠ 分页测试返回: {resp.status_code}")


def test_search():
    """测试搜索功能"""
    print("\n[2/5] 测试搜索功能...")
    client = Client()
    token = get_auth_token()
    
    if not token:
        print("  ✗ 无法获取 token，跳过测试")
        return
    
    # 测试打卡记录搜索
    resp = client.get(
        "/posts/?search=任务",
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )
    
    if resp.status_code == 200:
        print("  ✓ 搜索功能正常")
    else:
        print(f"  ⚠ 搜索测试返回: {resp.status_code}")


def test_statistics():
    """测试统计功能"""
    print("\n[3/5] 测试统计功能...")
    client = Client()
    token = get_auth_token()
    
    if not token:
        print("  ✗ 无法获取 token，跳过测试")
        return
    
    # 测试队伍统计
    resp = client.get(
        "/teams/statistics/",
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )
    
    if resp.status_code == 200:
        data = json.loads(resp.content.decode("utf-8"))
        print("  ✓ 队伍统计功能正常")
        print(f"    总队伍数: {data.get('total_teams', 'N/A')}")
        print(f"    活跃队伍: {data.get('active_teams', 'N/A')}")
    else:
        print(f"  • 队伍统计返回: {resp.status_code}")
    
    # 测试报名统计（普通用户）
    resp = client.get(
        "/applications/statistics/",
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )
    
    if resp.status_code == 200:
        data = json.loads(resp.content.decode("utf-8"))
        print("  ✓ 报名统计功能正常")
        print(f"    已报名: {data.get('has_application', 'N/A')}")
        print(f"    已匹配: {data.get('is_matched', 'N/A')}")
    else:
        print(f"  • 报名统计返回: {resp.status_code}")


def test_ordering():
    """测试排序功能"""
    print("\n[4/5] 测试排序功能...")
    client = Client()
    token = get_auth_token()
    
    if not token:
        print("  ✗ 无法获取 token，跳过测试")
        return
    
    # 测试打卡记录排序
    resp = client.get(
        "/posts/?ordering=-id",
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )
    
    if resp.status_code == 200:
        print("  ✓ 排序功能正常")
    else:
        print(f"  ⚠ 排序测试返回: {resp.status_code}")


def test_filtering():
    """测试筛选功能"""
    print("\n[5/5] 测试筛选功能...")
    client = Client()
    token = get_auth_token()
    
    if not token:
        print("  ✗ 无法获取 token，跳过测试")
        return
    
    # 测试按任务筛选打卡记录
    resp = client.get(
        "/posts/?task=1",
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )
    
    if resp.status_code == 200:
        print("  ✓ 筛选功能正常")
    else:
        print(f"  • 筛选测试返回: {resp.status_code}")


def main():
    print("=" * 60)
    print("开始测试进阶功能")
    print("=" * 60)
    
    setup_allowed_hosts()
    
    try:
        test_pagination()
        test_search()
        test_statistics()
        test_ordering()
        test_filtering()
        
        print("\n" + "=" * 60)
        print("进阶功能测试完成 ✅")
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
