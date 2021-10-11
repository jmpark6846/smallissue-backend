# Generated by Django 3.2.7 on 2021-10-10 06:39

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('issue', '0033_auto_20211010_1359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='users',
            field=models.ManyToManyField(blank=True, null=True, related_name='project_teams', to=settings.AUTH_USER_MODEL),
        ),
    ]