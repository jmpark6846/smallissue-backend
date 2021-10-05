# Generated by Django 3.2.7 on 2021-10-05 02:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('issue', '0018_rename_object_id_issuehistory_issue_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='issuehistory',
            old_name='issue_id',
            new_name='history_id',
        ),
        migrations.AddField(
            model_name='issuehistory',
            name='issue',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='issue.issue'),
            preserve_default=False,
        ),
    ]