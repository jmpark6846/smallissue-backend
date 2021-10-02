from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from issue.models import Project, Issue
from issue.permissions import ProjectTeammateOnly, ProjectLeaderOnly
from issue.serializers import ProjectSerializer, IssueSerializer, ProjectUserSerializer, IssueDetailSerializer, \
    ProjectAssigneeListSerializer


class ProjectViewSet(ModelViewSet):
    serializer_class = ProjectSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'users']:
            permission_classes = [ProjectTeammateOnly, IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action in ['destroy', 'update', 'partial_update']:
            permission_classes = [ProjectLeaderOnly, IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return self.request.user.projects.order_by('-created_at')

    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        project = self.get_object()
        users = ProjectAssigneeListSerializer(project.users, many=True).data
        return Response({'users': users})


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
        return Issue.objects.filter(project=self.kwargs['project_pk'], deleted_at=None).order_by('created_at')

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update']:
            return IssueDetailSerializer
        return IssueSerializer
    #
    # @action(detail=True, methods=['patch'])
    # def update_from_list(self, request, **kwargs):
    #     issue = self.get_object()
    #     serializer = IssueUpdateFromListSerializer(issue, data=request.data, partial=True)
    #     print(request.data)
    #
    #     try:
    #         serializer.is_valid(raise_exception=True)
    #         print(serializer.validated_data)
    #         serializer.save()
    #     except ValidationError:
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #
    #     return Response(serializer.data)