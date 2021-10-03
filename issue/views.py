from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from issue.models import Project, Issue
from issue.permissions import ProjectTeammateOnly, ProjectLeaderOnly, IsAuthorOnly
from issue.serializers import ProjectSerializer, IssueSerializer, ProjectUserSerializer, IssueDetailSerializer, \
    ProjectAssigneeListSerializer, CommentSerializer


class ProjectViewSet(ModelViewSet):
    serializer_class = ProjectSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'users']:
            permission_classes = [ProjectTeammateOnly, IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action in ['destroy', 'update', 'set_orders']:
            permission_classes = [ProjectLeaderOnly, IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return self.request.user.projects.order_by('order')

    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        project = self.get_object()
        users = ProjectAssigneeListSerializer(project.users, many=True).data
        return Response({'users': users})

    @action(detail=False, methods=['patch'])
    def set_orders(self, request, **kwargs):
        projects = self.get_queryset()
        new_orders = {}
        for i, id in enumerate(request.data.get('new_orders')):
            new_orders[int(id)] = i

        for project in projects:
            project.order = new_orders[project.id]
            project.save()

        return Response(status=200)


@api_view(['GET'])
def check_project_key_available(request: Request):
    key = request.query_params.get('key')

    if not isinstance(key, str):
        return Response(data={'available': False, 'error_msg': '문자가 아닙니다.'})

    import string
    key = key.upper()
    if not key.isascii() or not key[0] in string.ascii_uppercase:
        return Response(data={'available': False, 'error_msg': '영문자, 숫자, 특수문자만 사용할 수 있으며 첫 문자는 영문자여야 합니다.'})

    if request.user.projects.filter(key=key).exists():
        return Response(data={'available': False, 'error_msg': '프로젝트에서 이미 사용하고 있는 키값입니다.'})

    return Response(data={'available': True})


class ProjectIssueViewSet(ModelViewSet):
    permission_classes = [ProjectTeammateOnly, IsAuthenticated]

    def get_queryset(self):
        return Issue.objects.filter(project=self.kwargs['project_pk'], deleted_at=None).order_by('order')

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update']:
            return IssueDetailSerializer
        return IssueSerializer

    @action(detail=False, methods=['patch'])
    def set_orders(self, request, **kwargs):
        issues = self.get_queryset()
        new_orders = {}
        for i, id in enumerate(request.data.get('new_orders')):
            new_orders[int(id)] = i

        for issue in issues:
            issue.order = new_orders[issue.id]
            issue.save()

        return Response(status=200)


class ProjectCommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [ProjectTeammateOnly, IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [ProjectTeammateOnly, IsAuthenticated]
        elif self.action in ['destroy', 'update', 'partial_update']:
            permission_classes = [IsAuthorOnly, IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return Issue.objects.get(id=self.kwargs['issue_pk'], deleted_at=None).comments.filter(deleted_at=None).order_by('-created_at')
