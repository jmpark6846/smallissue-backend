from django.urls import path
from rest_framework import routers
from issue.views import ProjectViewSet

router = routers.SimpleRouter()
router.register('projects', ProjectViewSet, basename='project')
urlpatterns = [

] + router.urls

print(router.urls)