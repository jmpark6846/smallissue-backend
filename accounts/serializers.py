from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.models import User
from issue.models import IssueHistory


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'email', 'username', 'is_staff', 'is_active','date_joined', 'last_login']


class DisplayUserSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField()


class NotificationSerializer(serializers.Serializer):
    actor = DisplayUserSerializer(get_user_model(), read_only=True)
    unread = serializers.BooleanField()
    timestamp = serializers.DateTimeField()
    data = serializers.JSONField()
    description = serializers.CharField()


