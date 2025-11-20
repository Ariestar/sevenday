"""
初始化打卡任务
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from tasks.models import Task


class Command(BaseCommand):
    help = '初始化打卡任务列表'

    def handle(self, *args, **options):
        # 任务列表
        tasks_data = [
            {
                'title': '有趣一幕⭐',
                'introduction': '用图片或视频分享最近课上有趣的一幕，说说为什么有趣',
                'score': 100,
            },
            {
                'title': '锐评食堂⭐',
                'introduction': '锐评自己学部的食堂',
                'score': 100,
            },
            {
                'title': '分享梗图⭐',
                'introduction': '分享自己专业的梗图，并解释何意味',
                'score': 100,
            },
            {
                'title': '分享课表⭐',
                'introduction': '给对方看自己的课表，谈谈一天的感受',
                'score': 100,
            },
            {
                'title': '专业BGM⭐',
                'introduction': '如果用一首歌形容你上专业课/写专业课作业时的状态/心情，你会选择哪首歌?',
                'score': 100,
            },
            {
                'title': '学习苦恼⭐',
                'introduction': '分享经历：学习过程中有什么苦恼吗？最后是怎么解决的？',
                'score': 100,
            },
            {
                'title': '专业趣闻⭐',
                'introduction': '分享自己专业内的趣闻',
                'score': 100,
            },
            {
                'title': '专业书籍推荐⭐⭐',
                'introduction': '给对方推荐自己专业的一本经典，说说为什么推荐',
                'score': 200,
            },
            {
                'title': '专业误解⭐⭐',
                'introduction': '分享对自身专业的误解（如：上课内容、难度、就业及刻板印象）',
                'score': 200,
            },
            {
                'title': '印象深刻的专业课⭐⭐',
                'introduction': '向对方讲述自己印象深刻的一门专业课，说说为什么',
                'score': 200,
            },
            {
                'title': '喜欢的专业课老师⭐⭐',
                'introduction': '向对方介绍一位自己喜欢的专业课老师，说说为什么',
                'score': 200,
            },
            {
                'title': '看看广场⭐⭐',
                'introduction': '去"专交遇见你"的广场看看其他队伍的打卡，留下友爱互动',
                'score': 200,
            },
            {
                'title': '跨专业课程推荐⭐⭐',
                'introduction': '推荐一门本院适合跨专业学习的课程，并说明推荐理由',
                'score': 200,
            },
            {
                'title': 'WHY PICK ME⭐⭐',
                'introduction': '说说为什么想了解对方的专业',
                'score': 200,
            },
            {
                'title': '线下活动⭐⭐⭐',
                'introduction': '一起参加 "专交遇见你" 的线下活动',
                'score': 300,
            },
            {
                'title': '介绍培养方案⭐⭐⭐',
                'introduction': '给对方介绍自己的培养方案',
                'score': 300,
            },
            {
                'title': '一起自习⭐⭐⭐',
                'introduction': '线下/线上一起自习一次',
                'score': 300,
            },
            {
                'title': '专业未来发展方向⭐⭐⭐',
                'introduction': '向对方介绍自己专业未来的发展方向',
                'score': 300,
            },
            {
                'title': '共同听课⭐⭐⭐',
                'introduction': '一起听一堂课，课后交流听课感受与收获',
                'score': 300,
            },
            {
                'title': '交换礼物⭐⭐⭐',
                'introduction': '结束时给对方送一份礼物，感谢ta的陪伴~',
                'score': 300,
            },
        ]

        # 计算时间范围（从今天开始，每个任务持续7天）
        today = timezone.now().date()
        start_date = today
        
        # 删除所有现有任务
        Task.objects.all().delete()
        self.stdout.write(self.style.WARNING('已删除所有现有任务'))

        # 创建新任务
        created_count = 0
        for idx, task_data in enumerate(tasks_data, start=1):
            # 每个任务从今天开始，持续30天（足够长的时间）
            task_start = start_date
            task_end = start_date + timedelta(days=30)
            
            # 创建任务（cover字段现在可以为空）
            task = Task.objects.create(
                title=task_data['title'],
                introduction=task_data['introduction'],
                score=task_data['score'],
                start_time=task_start,
                end_time=task_end,
                # cover字段可以为空，后续可以通过admin后台上传
            )
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'✓ 创建任务 {idx}: {task.title} (ID: {task.id})')
            )

        self.stdout.write(
            self.style.SUCCESS(f'\n成功创建 {created_count} 个任务！')
        )

