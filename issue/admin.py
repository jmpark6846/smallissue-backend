from django.contrib import admin
from issue.models import Project, Issue, Comment
from simple_history.admin import SimpleHistoryAdmin

admin.site.register(Project)
admin.site.register(Issue, SimpleHistoryAdmin)
admin.site.register(Comment)