from django.contrib import admin
from issue.models import Project, Issue, Comment, Team, Participation
from simple_history.admin import SimpleHistoryAdmin

admin.site.register(Project)
admin.site.register(Team)
admin.site.register(Participation)
admin.site.register(Issue, SimpleHistoryAdmin)
admin.site.register(Comment)