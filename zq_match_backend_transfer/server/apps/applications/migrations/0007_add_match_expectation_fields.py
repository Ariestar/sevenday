# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('academies', '0002_data_initial'),
        ('applications', '0006_matchattempt'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='degree_choice',
            field=models.CharField(blank=True, default='', help_text='本科/研究生', max_length=20, verbose_name='期望同伴学历'),
        ),
        migrations.AddField(
            model_name='application',
            name='major_category_choice',
            field=models.CharField(blank=True, default='', max_length=50, verbose_name='期望同伴大类'),
        ),
        migrations.AddField(
            model_name='application',
            name='college_choice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='college_choice_applications', to='academies.academy', verbose_name='期望同伴学院'),
        ),
    ]


