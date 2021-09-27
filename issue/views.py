from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from issue.models import Project
from issue.permissions import ProjectTeammateOnly, ProjectLeaderOnly
from issue.serializers import ProjectSerializer


class ProjectViewSet(ModelViewSet):
    serializer_class = ProjectSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [ProjectTeammateOnly]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action in ['destroy', 'update', 'partial_update']:
            permission_classes = [ProjectLeaderOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        # return Project.objects.all()
        return self.request.user.projects.order_by('-created_at')
