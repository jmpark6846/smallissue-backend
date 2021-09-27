from django.urls import path
from rest_framework import routers
from issue.views import ProjectViewSet, check_project_key_available

router = routers.SimpleRouter()
router.register('projects', ProjectViewSet, basename='project')

urlpatterns = [
    path('projects/check_project_key_available/', check_project_key_available)
] + router.urls
