# Generated migration for adding PostLike and PostComment models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0001_initial'),
    ]

    operations = [
        # 添加Post模型的时间字段
        migrations.AddField(
            model_name='post',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='创建时间'),
        ),
        migrations.AddField(
            model_name='post',
            name='update_time',
            field=models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name='更新时间'),
        ),
        # 创建PostLike模型
        migrations.CreateModel(
            name='PostLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='点赞时间')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='posts.post', verbose_name='打卡记录')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_likes', to=settings.AUTH_USER_MODEL, verbose_name='点赞用户')),
            ],
            options={
                'verbose_name': '打卡点赞',
                'verbose_name_plural': '打卡点赞',
                'db_table': 'zq_match_post_like',
            },
        ),
        # 创建PostComment模型
        migrations.CreateModel(
            name='PostComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(max_length=500, verbose_name='评论内容')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='评论时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='posts.post', verbose_name='打卡记录')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_comments', to=settings.AUTH_USER_MODEL, verbose_name='评论用户')),
            ],
            options={
                'verbose_name': '打卡评论',
                'verbose_name_plural': '打卡评论',
                'db_table': 'zq_match_post_comment',
                'ordering': ['create_time'],
            },
        ),
        # 添加唯一约束：每个用户对每个打卡只能点赞一次
        migrations.AlterUniqueTogether(
            name='postlike',
            unique_together={('post', 'user')},
        ),
    ]

