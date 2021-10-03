from rest_framework.permissions import BasePermission

from issue.models import Issue, Project, Comment


class ProjectTeammateOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Issue):
            return obj.project.users.filter(id=request.user.id).exists()
        elif isinstance(obj, Project):
            return obj.users.filter(id=request.user.id).exists()

        return False


class ProjectLeaderOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.leader == request.user


class IsAuthorOnly(BasePermission):
    def has_object_permission(self, request, view, obj: Comment):
        return obj.author == request.user