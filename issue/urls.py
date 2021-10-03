from django.urls import path, include
from rest_framework_nested import routers
from issue.views import ProjectViewSet, check_project_key_available, ProjectIssueViewSet, ProjectCommentViewSet

router = routers.SimpleRouter()
router.register(r'projects', ProjectViewSet, basename='project')

project_router = routers.NestedSimpleRouter(router, r'projects', lookup='project')
project_router.register(r'issues', ProjectIssueViewSet, basename='project-issues')

issue_router = routers.NestedSimpleRouter(project_router, 'issues', lookup='issue')
issue_router.register('comments', ProjectCommentViewSet, basename='issue-comments')

urlpatterns = [
    path('projects/check_project_key_available/', check_project_key_available), # router url 보다 상위에 올 것
    path(r'', include(router.urls)),
    path(r'', include(project_router.urls)),
    path(r'', include(issue_router.urls))
]
