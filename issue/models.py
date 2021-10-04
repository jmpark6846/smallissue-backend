from django.conf import settings
from django.db import models
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
