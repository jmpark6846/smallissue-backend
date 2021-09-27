from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from issue.permissions import ProjectTeammateOnly
from issue.serializers import ProjectSerializer


class ProjectViewSet(ModelViewSet):
    permission_classes = ProjectTeammateOnly
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return self.request.user.projects
