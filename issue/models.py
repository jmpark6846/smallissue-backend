from notifications.signals import notify

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
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, related_name='assigned_issues',
                                 null=True)
    subscribers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='subscribed_issues',
                                         through='IssueSubscription', blank=True)
    status = models.SmallIntegerField(choices=STATUS.choices, default=STATUS.TODO)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='issues')
    order = models.PositiveSmallIntegerField(null=True)
    tags = models.ManyToManyField('issue.Tag', related_name='issues', through='IssueTagging',
                                  through_fields=('issue', 'tag'))
    history = HistoricalRecords()

    def __str__(self):
        return '#{}: {}'.format(self.id, self.title)


def generate_key(sender, instance, created, **kwargs):
    if created:
        instance.key = instance.project.key + '-' + str(instance.id)
        instance.save()


def subscribe_author_when_created(sender, instance: Issue, created, **kwargs):
    if created:
        instance.subscribers.add(instance.author)


post_save.connect(generate_key, sender=Issue)
post_save.connect(subscribe_author_when_created, sender=Issue)


class IssueSubscription(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    subscriber = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


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
    history_id = models.PositiveIntegerField()
    issue_id = models.PositiveIntegerField(blank=True, null=True)
    history = GenericForeignKey('content_type', 'history_id')
    history_date = models.DateTimeField(null=True)

    class Meta:
        ordering = ['-history_date']


def notify_issue_changes(sender, instance, created, **kwargs):
    issue = Issue.objects.get(id=instance.issue_id)
    actor = instance.history.history_user
    issue_subscribers = issue.subscribers.exclude(id=actor.id)

    if not issue_subscribers.exists():
        return

    h = instance.history

    if h.__class__ == Issue.history.model:  # HistoricalIssue
        if h.history_type == "+":
            description = "이슈가 생성되었습니다."
            verb = "생성"
        elif h.history_type == "-":
            description = "이슈가 삭제되었습니다."
            verb = "삭제"
        else:  # h.history_type == "~"
            description = "이슈가 업데이트 되었습니다."
            verb = "업데이트"
    else:  # HistoricalIssueTagging, 태그는 추가, 삭제 모두 이슈 업데이트로 알림.
        description = "이슈가 업데이트 되었습니다."
        verb = "업데이트"

    notify.send(actor, recipient=issue_subscribers, verb=verb, target=instance,
                description=description)


post_save.connect(notify_issue_changes, sender=IssueHistory)


def create_issue_history(sender, instance, created, **kwargs):
    content_type = ContentType.objects.get_for_model(instance)

    if sender == Issue.history.model:
        issue_id = instance.id
    elif sender == IssueTagging.history.model:
        issue_id = instance.issue_id
    else:
        raise TypeError('이슈와 이슈태깅 히스토리컬 모델이 아닙니다.')

    try:
        issue_history = IssueHistory.objects.get(
            content_type=content_type,
            history_id=instance.history_id,
            issue_id=issue_id
        )
    except IssueHistory.DoesNotExist:
        issue_history = IssueHistory(
            content_type=content_type,
            history_id=instance.history_id,
            issue_id=issue_id
        )

    issue_history.history_date = instance.history_date
    issue_history.save()


post_save.connect(create_issue_history, sender=Issue.history.model)
post_save.connect(create_issue_history, sender=IssueTagging.history.model)
