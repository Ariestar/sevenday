# Generated migration
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='cover',
            field=models.ImageField(blank=True, null=True, upload_to='task\\cover', verbose_name='封面'),
        ),
    ]

