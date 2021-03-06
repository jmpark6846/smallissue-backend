# Generated by Django 3.2.7 on 2021-10-05 06:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('issue', '0021_auto_20211005_1459'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalissue',
            name='author',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='issue',
            name='author',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='accounts.user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='issue',
            name='subscribers',
            field=models.ManyToManyField(related_name='subscribed_issues', to=settings.AUTH_USER_MODEL),
        ),
    ]
