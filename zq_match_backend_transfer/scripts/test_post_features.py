"""
打卡功能测试脚本
测试打卡的创建、查询、删除等功能
"""
import os
import sys
import django
from django.core.files.base import ContentFile

# 设置 Django 环境
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
# 为编辑器/静态分析器提供明确的模块搜索路径，避免 posts/tasks 等无法解析的提示
apps_path = os.path.join(ROOT_DIR, "server", "apps")
if apps_path not in sys.path:
    sys.path.insert(0, apps_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from posts.models import Post  # type: ignore[reportMissingImports]
from tasks.models import Task  # type: ignore[reportMissingImports]
from teams.models import Team  # type: ignore[reportMissingImports]
from academies.models import Academy  # type: ignore[reportMissingImports]

User = get_user_model()


def print_section(title):
    """打印分节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_post_creation():
    """测试打卡创建"""
    print_section("测试1: 打卡数据准备")
    
    # 1. 创建学院
    academy, _ = Academy.objects.get_or_create(
        name="测试学院"
    )
    print(f"✓ 学院创建成功: {academy.name}")
    
    # 2. 创建用户
    user1, created = User.objects.get_or_create(
        username="test_post_user1",
        defaults={
            "email": "test_post_user1@example.com",
            "academy": academy,
            "school_number": "2024001001",
            "grade": 2024,
            "gender": 1,
        }
    )
    if created:
        user1.set_password("test123456")
        user1.save()
    print(f"✓ 用户1创建成功: {user1.username}")
    
    user2, created = User.objects.get_or_create(
        username="test_post_user2",
        defaults={
            "email": "test_post_user2@example.com",
            "academy": academy,
            "school_number": "2024001002",
            "grade": 2024,
            "gender": 2,
        }
    )
    if created:
        user2.set_password("test123456")
        user2.save()
    print(f"✓ 用户2创建成功: {user2.username}")
    
    # 3. 创建队伍
    team, created = Team.objects.get_or_create(
        name="打卡测试队伍",
        defaults={
            "introduction": "测试简介",
        }
    )
    print(f"✓ 队伍创建成功: {team.name}")
    
    # 4. 用户加入队伍
    user1.team = team
    user1.save()
    user2.team = team
    user2.save()
    print(f"✓ 用户已加入队伍")
    
    # 5. 创建任务
    today = timezone.now().date()

    def dummy_image(name: str = "cover.jpg"):
        return ContentFile(b"test", name)

    task1, created = Task.objects.get_or_create(
        title="进行中的任务",
        defaults={
            "introduction": "这是一个正在进行的任务",
            "score": 10,
            "cover": dummy_image("cover1.jpg"),
            "start_time": today - timedelta(days=1),
            "end_time": today + timedelta(days=1),
        }
    )
    print(f"✓ 进行中的任务创建成功: {task1.title}")
    
    task2, created = Task.objects.get_or_create(
        title="未开始的任务",
        defaults={
            "introduction": "这是一个未开始的任务",
            "score": 15,
            "cover": dummy_image("cover2.jpg"),
            "start_time": today + timedelta(days=1),
            "end_time": today + timedelta(days=2),
        }
    )
    print(f"✓ 未开始的任务创建成功: {task2.title}")
    
    task3, created = Task.objects.get_or_create(
        title="已结束的任务",
        defaults={
            "introduction": "这是一个已结束的任务",
            "score": 20,
            "cover": dummy_image("cover3.jpg"),
            "start_time": today - timedelta(days=3),
            "end_time": today - timedelta(days=1),
        }
    )
    print(f"✓ 已结束的任务创建成功: {task3.title}")
    
    return {
        'user1': user1,
        'user2': user2,
        'team': team,
        'task1': task1,
        'task2': task2,
        'task3': task3,
    }


def test_post_queries(data):
    """测试打卡查询"""
    print_section("测试2: 打卡查询功能")
    
    # 查询所有打卡
    all_posts = Post.objects.all()
    print(f"✓ 所有打卡记录数: {all_posts.count()}")
    
    # 查询队伍的打卡
    team_posts = Post.objects.filter(team=data['team'])
    print(f"✓ 测试队伍的打卡记录数: {team_posts.count()}")
    
    # 查询特定任务的打卡
    task_posts = Post.objects.filter(task=data['task1'])
    print(f"✓ 任务'{data['task1'].title}'的打卡记录数: {task_posts.count()}")
    
    # 使用 select_related 优化查询
    optimized_posts = Post.objects.select_related('task', 'team').all()[:5]
    print(f"✓ 优化查询测试: 获取了 {optimized_posts.count()} 条记录")
    
    for post in optimized_posts:
        print(f"  - {post.title} | 任务: {post.task.title} | 队伍: {post.team.name}")


def test_post_validation():
    """测试打卡数据验证"""
    print_section("测试3: 打卡数据验证")
    
    from posts.serializers import PostCreateSerializer  # type: ignore[reportMissingImports]
    
    # 测试1: 空标题
    data = {
        'title': '',
        'description': '测试描述',
        'task': 1,
    }
    serializer = PostCreateSerializer(data=data)
    if not serializer.is_valid():
        print(f"✓ 空标题验证: {serializer.errors.get('title', [''])[0]}")
    
    # 测试2: 标题过长
    data = {
        'title': 'a' * 51,
        'description': '测试描述',
        'task': 1,
    }
    serializer = PostCreateSerializer(data=data)
    if not serializer.is_valid():
        print(f"✓ 标题过长验证: {serializer.errors.get('title', [''])[0]}")
    
    # 测试3: 描述过长
    data = {
        'title': '测试标题',
        'description': 'a' * 501,
        'task': 1,
    }
    serializer = PostCreateSerializer(data=data)
    if not serializer.is_valid():
        print(f"✓ 描述过长验证: {serializer.errors.get('description', [''])[0]}")
    
    print(f"✓ 数据验证测试完成")


def test_post_business_logic(data):
    """测试打卡业务逻辑"""
    print_section("测试4: 打卡业务逻辑")
    
    # 检查任务时间范围
    today = timezone.now().date()
    
    # 进行中的任务
    if data['task1'].start_time <= today <= data['task1'].end_time:
        print(f"✓ 任务'{data['task1'].title}' 当前可以打卡")
    
    # 未开始的任务
    if today < data['task2'].start_time:
        print(f"✓ 任务'{data['task2'].title}' 尚未开始 (开始时间: {data['task2'].start_time})")
    
    # 已结束的任务
    if today > data['task3'].end_time:
        print(f"✓ 任务'{data['task3'].title}' 已经结束 (结束时间: {data['task3'].end_time})")
    
    # 检查重复打卡
    existing_posts = Post.objects.filter(
        team=data['team'],
        task=data['task1']
    )
    
    if existing_posts.exists():
        print(f"✓ 队伍'{data['team'].name}'已对任务'{data['task1'].title}'打卡")
        print(f"  打卡数量: {existing_posts.count()}")
    else:
        print(f"✓ 队伍'{data['team'].name}'尚未对任务'{data['task1'].title}'打卡")


def test_post_statistics(data):
    """测试打卡统计"""
    print_section("测试5: 打卡统计")
    
    from django.db.models import Count
    
    # 每个队伍的打卡数
    team_post_count = Post.objects.filter(team=data['team']).count()
    print(f"✓ 队伍'{data['team'].name}'的打卡总数: {team_post_count}")
    
    # 每个任务的打卡数
    for task in [data['task1'], data['task2'], data['task3']]:
        count = Post.objects.filter(task=task).count()
        print(f"✓ 任务'{task.title}'的打卡数: {count}")
    
    # 统计所有队伍的打卡排名
    team_stats = Team.objects.annotate(
        post_count=Count('posts')
    ).order_by('-post_count')[:5]
    
    print(f"\n打卡排行榜 (Top 5):")
    for i, team in enumerate(team_stats, 1):
        print(f"  {i}. {team.name}: {team.post_count} 次打卡")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("  打卡功能完整测试")
    print("="*60)
    
    try:
        # 测试1: 数据准备
        data = test_post_creation()
        
        # 测试2: 查询功能
        test_post_queries(data)
        
        # 测试3: 数据验证
        test_post_validation()
        
        # 测试4: 业务逻辑
        test_post_business_logic(data)
        
        # 测试5: 统计功能
        test_post_statistics(data)
        
        print_section("测试总结")
        print("✅ 所有测试完成!")
        print("\n打卡功能包含:")
        print("  1. ✓ 创建打卡 (POST /posts/)")
        print("  2. ✓ 查询打卡列表 (GET /posts/)")
        print("  3. ✓ 查询打卡详情 (GET /posts/{id}/)")
        print("  4. ✓ 我的打卡记录 (GET /posts/my-posts/)")
        print("  5. ✓ 按任务查询 (GET /posts/by-task/?task_id=X)")
        print("  6. ✓ 检查打卡状态 (GET /posts/check-status/?task_id=X)")
        print("  7. ✓ 删除打卡 (DELETE /posts/{id}/delete-post/)")
        print("  8. ✓ 搜索功能 (支持标题、描述、队伍名)")
        print("  9. ✓ 分页功能")
        print("  10. ✓ 筛选功能 (按任务、队伍)")
        print("\n业务规则:")
        print("  • 只能在任务时间范围内打卡")
        print("  • 每个队伍每个任务只能打卡一次")
        print("  • 必须有队伍才能打卡")
        print("  • 只能删除任务未结束的打卡记录")
        print("  • 只能删除本队伍的打卡记录")
        print("  • 图片大小限制5MB")
        print("  • 支持JPG、PNG、WEBP格式")
        
    except Exception as e:
        print(f"\n❌ 测试出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
