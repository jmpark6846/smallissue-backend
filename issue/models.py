from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from simple_history.models import HistoricalRecords
from smallissue.models import BaseModel


class Project(BaseModel):
    key = models.CharField(max_length=5)
    name = models.CharField(max_length=128)
    leader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, related_name='projects_leading')
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='projects')
    order = models.PositiveSmallIntegerField(null=True)

    def __str__(self):
        return self.name


class Issue(BaseModel):
    class STATUS(models.IntegerChoices):
        TODO = 0
        DOING = 1
        DONE = 2

    key = models.CharField(max_length=20, null=True)
    title = models.CharField(max_length=128)
    body = models.TextField(null=True, blank=True)
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, related_name='assigned_issues',
                                 null=True)
    status = models.SmallIntegerField(choices=STATUS.choices, default=STATUS.TODO)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='issues')
    order = models.PositiveSmallIntegerField(null=True)
    tags = models.ManyToManyField('issue.Tag', related_name='issues', through='IssueTagging',
                                  through_fields=('issue', 'tag'))
    history = HistoricalRecords()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.key:
            new_count = Issue.objects.filter(project=self.project).count() + 1
            self.key = self.project.key + '-' + str(new_count)

        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return '#{}: {}'.format(self.id, self.title)


class Comment(BaseModel):
    content = models.TextField()
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='issue_comments')


class Tag(models.Model):
    name = models.CharField(max_length=30)


class IssueTagging(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    history = HistoricalRecords()


class IssueHistory(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(null=True)

    class Meta:
        ordering = ['-created_at']


def create_issue_history(sender, instance, created, **kwargs):
    content_type = ContentType.objects.get_for_model(instance)
    try:
        issue_history = IssueHistory.objects.get(
            content_type=content_type,
            object_id=instance.id
        )
    except IssueHistory.DoesNotExist:
        issue_history = IssueHistory(
            content_type=content_type,
            object_id=instance.id
        )


    issue_history.created_at = instance.history_date
    issue_history.save()


post_save.connect(create_issue_history, sender=Issue.history.model)
post_save.connect(create_issue_history, sender=IssueTagging.history.model)