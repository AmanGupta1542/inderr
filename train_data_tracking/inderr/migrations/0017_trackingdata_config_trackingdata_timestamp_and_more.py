# Generated by Django 5.0.2 on 2024-05-31 13:06

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inderr', '0016_logininfo'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='trackingdata',
            name='config',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='inderr.configinfo'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='trackingdata',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='trackingdata',
            name='user',
            field=models.ForeignKey(default=79, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
