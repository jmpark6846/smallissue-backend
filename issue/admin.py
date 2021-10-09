from django.contrib import admin
from issue.models import Project, Issue, Comment, UserRole, Participation
from simple_history.admin import SimpleHistoryAdmin

admin.site.register(Project)
admin.site.register(UserRole)
admin.site.register(Participation)
admin.site.register(Issue, SimpleHistoryAdmin)
admin.site.register(Comment)