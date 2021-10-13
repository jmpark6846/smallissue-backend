from django.urls import path, include
from rest_framework_nested import routers
from issue.views import ProjectViewSet, check_project_key_available, ProjectIssueViewSet, ProjectCommentViewSet, \
    ProjectParticipationViewSet, ProjectTeamViewSet, ProjectTeamUsersViewSet, AttachmentViewSet

router = routers.SimpleRouter()
router.register(r'projects', ProjectViewSet, basename='project')

project_router = routers.NestedSimpleRouter(router, r'projects', lookup='project')
project_router.register(r'issues', ProjectIssueViewSet, basename='project-issues')
project_router.register(r'participations', ProjectParticipationViewSet, basename='project-participations')
project_router.register(r'teams', ProjectTeamViewSet, basename='project-teams')
project_router.register(r'attachments', AttachmentViewSet, basename='project-attachments')

issue_router = routers.NestedSimpleRouter(project_router, 'issues', lookup='issue')
issue_router.register('comments', ProjectCommentViewSet, basename='issue-comments')

teams_router = routers.NestedSimpleRouter(project_router, 'teams', lookup='team')
teams_router.register('users', ProjectTeamUsersViewSet, basename='team-users')

urlpatterns = [
    path('projects/check_project_key_available/', check_project_key_available),  # router url 보다 상위에 올 것
    path(r'', include(router.urls)),
    path(r'', include(project_router.urls)),
    path(r'', include(issue_router.urls)),
    path(r'', include(teams_router.urls))
]
