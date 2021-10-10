from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.serializers import UserDetailSerializer
from issue.models import Project, Issue, Comment, Tag, Team


class ProjectSerializer(serializers.ModelSerializer):
    key = serializers.CharField(read_only=True)

    class Meta:
        model = Project
        fields = '__all__'

    def to_internal_value(self, data):
        User = get_user_model()
        try:
            user = User.objects.get(pk=data['leader']['id'])
        except User.DoesNotExist:
            raise ValueError('user does not exist')

        data['leader'] = user
        return data

    def to_representation(self, instance: Project):
        result = super(ProjectSerializer, self).to_representation(instance)
        result['leader'] = {'id': instance.leader.id, 'username': instance.leader.username}
        return result

    def create(self, validated_data):
        validated_data['order'] = Project.objects.count()
        return super(ProjectSerializer, self).create(validated_data)


class ProjectUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username']


class IssueSerializer(serializers.ModelSerializer):
    key = serializers.CharField(read_only=True)

    class Meta:
        model = Issue
        fields = '__all__'

    def create(self, validated_data):
        validated_data['order'] = Issue.objects.count()
        return super(IssueSerializer, self).create(validated_data)

    def to_representation(self, instance):
        result = super().to_representation(instance)

        if instance.assignee:
            result['assignee'] = {'id': instance.assignee.id, 'username': instance.assignee.username}
        else:
            result['assignee'] = None

        return result


class ProjectUsersSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.CharField()
    team = serializers.SerializerMethodField()
    participation = serializers.SerializerMethodField()

    def get_team(self, obj):
        team = obj.project_teams.filter(project=self.context.get('project')).last()
        if team:
            return {'id': team.id, 'name': team.name}
        else:
            return {'id': None, 'name':None}

    def get_participation(self, obj):
        project = self.context.get('project')
        p = obj.participation_set.filter(project=project).last()
        return {'id': p.id, 'project': {'id': project.id, 'name': project.name}, 'date_joined': p.date_joined,
                'job_title': p.job_title}


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'


class IssueDetailSerializer(serializers.ModelSerializer):
    key = serializers.CharField(read_only=True)

    class Meta:
        model = Issue
        fields = '__all__'

    def to_representation(self, instance):
        result = super(IssueDetailSerializer, self).to_representation(instance)
        result['project'] = {'name': instance.project.name, 'id': instance.project.id}

        tag_names = []
        qs = instance.tags.all()
        for tag in qs:
            tag_names.append(tag.name)
        result['tags'] = tag_names

        if instance.assignee:
            result['assignee'] = {'id': instance.assignee.id, 'username': instance.assignee.username}
        else:
            result['assignee'] = None

        return result


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

    def to_representation(self, instance: Comment):
        result = super(CommentSerializer, self).to_representation(instance)
        result['author'] = {'id': instance.author.pk, 'username': instance.author.username}
        return result
