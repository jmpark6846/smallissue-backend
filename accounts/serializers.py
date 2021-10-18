from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import serializers

from accounts.models import User, UserProfile
from issue.models import IssueHistory, Issue


class ProfileSerializer(serializers.ModelSerializer):
    file = serializers.ImageField(use_url=True)

    class Meta:
        model = UserProfile
        fields = ['file']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class UserDetailSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    is_readonly = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['pk', 'email', 'username', 'is_staff', 'is_active', 'date_joined', 'last_login', 'profile',
                  'is_readonly']

    def get_is_readonly(self, obj):
        return obj.groups.filter(name='read_only').exists()


class DisplayUserSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField()


class NotificationIssueHistorySerializer(serializers.Serializer):
    history_id = serializers.PrimaryKeyRelatedField(read_only=True)
    issue = serializers.SerializerMethodField()

    def get_issue(self, obj):
        try:
            issue = Issue.objects.get(id=obj.issue_id)
            # change = get_change_from_histories([obj])[0]
            return {'id': issue.id, 'key': issue.key, 'title': issue.title,
                    'project_id': issue.project.id}  # change

        except Issue.DoesNotExist:
            raise ValueError('알림의 이슈가 존재하지 않습니다.')


class NotificationSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    actor = DisplayUserSerializer(get_user_model(), read_only=True)
    unread = serializers.BooleanField()
    timestamp = serializers.DateTimeField()
    target = NotificationIssueHistorySerializer(IssueHistory)
    description = serializers.CharField()


class UserSearchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
