from rest_framework.permissions import BasePermission


class ProjectTeammateOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.users.filter(id=request.user.id).exists()


class ProjectLeaderOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.leader == request.user
