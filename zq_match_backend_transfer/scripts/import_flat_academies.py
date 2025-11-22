"""
导入平级院系数据的脚本
所有院系都是顶层（parent=None），没有层级结构
"""
import os
import sys
from pathlib import Path

# 用户提供的院系列表
ACADEMIES = [
    "文学院",
    "历史学院",
    "哲学学院",
    "外国语言文学学院",
    "新闻与传播学院",
    "艺术学院",
    "信息管理学院",
    "经济与管理学院",
    "法学院",
    "马克思主义学院",
    "社会学院",
    "政治与公共管理学院",
    "教育科学研究院",
    "数学与统计学院",
    "物理科学与技术学院",
    "化学与分子科学学院",
    "生命科学学院",
    "资源与环境科学学院",
    "动力与机械学院",
    "电气与自动化学院",
    "城市设计学院",
    "土木建筑工程学院",
    "水利水电学院",
    "电子信息学院",
    "计算机学院",
    "国家网络安全学院",
    "测绘学院",
    "遥感信息工程学院",
    "基础医学院",
    "健康学院",
    "药学院",
    "口腔医学院",
    "公共卫生学院",
    "护理学院",
]


def main():
    BASE = Path(__file__).resolve().parents[1]
    # 确保脚本静态分析与运行环境能解析顶级 apps 包
    apps_path = BASE / 'server' / 'apps'
    if str(BASE) not in sys.path:
        sys.path.insert(0, str(BASE))
    if str(apps_path) not in sys.path:
        sys.path.insert(0, str(apps_path))

    # Use Django ORM
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
    django.setup()
    from academies.models import Academy

    print(f'开始导入 {len(ACADEMIES)} 个院系...')
    
    # 先清空所有现有数据（可选，如果需要完全重置）
    # Academy.objects.all().delete()
    # print('已清空现有院系数据')
    
    created = 0
    updated = 0
    
    # 导入所有院系，所有都是顶层（parent=None, level=0）
    for idx, name in enumerate(ACADEMIES, start=1):
        # 清理名称（去除前后空格）
        name = name.strip()
        if not name:
            continue
            
        obj, is_new = Academy.objects.update_or_create(
            name=name,
            defaults={
                'name': name,
                'level': 0,
                'parent': None,
            },
        )
        if is_new:
            created += 1
            print(f'  ✓ 创建: {name}')
        else:
            updated += 1
            print(f'  ↻ 更新: {name}')

    print(f'\n导入完成！')
    print(f'  创建: {created} 个院系')
    print(f'  更新: {updated} 个院系')
    print(f'  总计: {Academy.objects.count()} 个院系')
    
    # 显示所有顶层院系
    top_level = Academy.objects.filter(parent=None).count()
    print(f'  顶层院系: {top_level} 个')


if __name__ == '__main__':
    main()

