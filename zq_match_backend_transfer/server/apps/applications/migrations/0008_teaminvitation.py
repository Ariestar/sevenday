# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('applications', '0007_add_match_expectation_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamInvitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', '待确认'), ('accepted', '已同意'), ('rejected', '已拒绝')], default='pending', max_length=20, verbose_name='邀请状态')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('invitee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_invitations', to=settings.AUTH_USER_MODEL, verbose_name='被邀请方')),
                ('inviter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_invitations', to=settings.AUTH_USER_MODEL, verbose_name='邀请方')),
            ],
            options={
                'verbose_name': '组队邀请',
                'verbose_name_plural': '组队邀请',
                'db_table': 'zq_match_team_invitation',
                'unique_together': {('inviter', 'invitee')},
            },
        ),
        migrations.AddIndex(
            model_name='teaminvitation',
            index=models.Index(fields=['invitee', 'status'], name='zq_match_te_invitee__idx'),
        ),
        migrations.AddIndex(
            model_name='teaminvitation',
            index=models.Index(fields=['inviter', 'status'], name='zq_match_te_inviter__idx'),
        ),
    ]









