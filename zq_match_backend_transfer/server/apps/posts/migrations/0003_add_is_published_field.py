# Generated migration for adding is_published field to Post model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_add_like_comment_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='is_published',
            field=models.BooleanField(default=False, verbose_name='是否发布到广场'),
        ),
    ]

