"""
Django 管理命令：导入平级院系数据
所有院系都是顶层（parent=None），没有层级结构
"""
from django.core.management.base import BaseCommand
from academies.models import Academy


class Command(BaseCommand):
    help = "导入平级院系数据（所有院系都是顶层，parent=None）"

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

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='清空所有现有院系数据后再导入',
        )

    def handle(self, *args, **options):
        clear_existing = options.get('clear', False)
        
        if clear_existing:
            count = Academy.objects.count()
            Academy.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'已清空 {count} 个现有院系数据'))
        
        self.stdout.write(f'开始导入 {len(self.ACADEMIES)} 个院系...')
        
        created = 0
        updated = 0
        
        # 导入所有院系，所有都是顶层（parent=None, level=0）
        for name in self.ACADEMIES:
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
                self.stdout.write(f'  ✓ 创建: {name}')
            else:
                updated += 1
                self.stdout.write(f'  ↻ 更新: {name}')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'导入完成！'))
        self.stdout.write(f'  创建: {created} 个院系')
        self.stdout.write(f'  更新: {updated} 个院系')
        
        total = Academy.objects.count()
        top_level = Academy.objects.filter(parent=None).count()
        self.stdout.write(f'  总计: {total} 个院系')
        self.stdout.write(f'  顶层院系: {top_level} 个')

