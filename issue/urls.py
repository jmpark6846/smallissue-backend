from django.urls import path, include
from rest_framework_nested import routers
from issue.views import ProjectViewSet, check_project_key_available, ProjectIssueViewSet

router = routers.SimpleRouter()
router.register(r'projects', ProjectViewSet, basename='project')

project_router = routers.NestedSimpleRouter(router, r'projects', lookup='project')
project_router.register(r'issues', ProjectIssueViewSet, basename='project-issues')

urlpatterns = [
    path(r'', include(router.urls)),
    path(r'', include(project_router.urls)),
    path('projects/check_project_key_available/', check_project_key_available)
]
