from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission

from issue.models import Issue, Project, Comment, Team, Participation

User = get_user_model()


class ProjectUsersOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Issue) or isinstance(obj, Team):
            return obj.project.users.filter(id=request.user.id).exists()

        elif isinstance(obj, Participation):
            return obj.project.filter(users__id=request.user.id).exists()

        elif isinstance(obj, Project):
            return obj.users.filter(id=request.user.id).exists()

        raise PermissionError('ProjectUsersOnly에 해당 뷰에 대한 권한 설정이 없습니다.')


class ProjectLeaderOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Participation):
            return obj.project.leader.id == request.user.id
        else:
            return obj.leader == request.user


class IsAuthorOnly(BasePermission):
    def has_object_permission(self, request, view, obj: Comment):
        return obj.author == request.user
