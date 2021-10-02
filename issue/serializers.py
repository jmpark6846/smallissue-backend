from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.serializers import UserDetailSerializer
from issue.models import Project, Issue


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

    def validate(self, data):
        user = data['leader']
        if user.projects.filter(key=data['key']).exists():
            raise serializers.ValidationError('key not available')

        return data


class ProjectUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username']


class IssueSerializer(serializers.ModelSerializer):
    key = serializers.CharField(read_only=True)

    class Meta:
        model = Issue
        fields = '__all__'

    def to_representation(self, instance):
        result = super().to_representation(instance)
        assignee_id = result['assignee']

        if assignee_id:
            User = get_user_model()
            assignee = User.objects.get(id=assignee_id)
            result['assignee'] = {'id': assignee_id, 'username': assignee.username}
        else:
            result['assignee'] = None

        return result


class ProjectAssigneeListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()


class IssueDetailSerializer(serializers.ModelSerializer):
    key = serializers.CharField(read_only=True)

    class Meta:
        model = Issue
        fields = '__all__'

    def to_representation(self, instance):
        result = super(IssueDetailSerializer, self).to_representation(instance)
        result['project'] = {'name': instance.project.name, 'id': instance.project.id}
        assignee_id = result['assignee']

        if assignee_id:
            User = get_user_model()
            assignee = User.objects.get(id=assignee_id)
            result['assignee'] = ProjectAssigneeListSerializer(assignee).data
        else:
            result['assignee'] = None

        return result
