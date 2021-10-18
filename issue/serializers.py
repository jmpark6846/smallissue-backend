from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from issue.models import Project, Issue, Comment, Tag, Team, Participation, Attachment

User = get_user_model()


class ProjectSerializer(serializers.ModelSerializer):
    key = serializers.CharField(read_only=True)

    class Meta:
        model = Project
        fields = '__all__'

    def to_internal_value(self, data):
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
        fields = ['id', 'username', 'email']


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


class ProjectParticipationSerializer(serializers.ModelSerializer):
    user = ProjectUserSerializer()
    team = serializers.SerializerMethodField()

    class Meta:
        model = Participation
        fields = '__all__'

    def get_team(self, obj: Participation):
        team = obj.user.project_teams.filter(project=obj.project).last()

        if team:
            return {'id': team.id, 'name': team.name}
        else:
            return {'id': None, 'name': None}


class TeamSerializer(serializers.ModelSerializer):
    users = ProjectUserSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = '__all__'

    def validate(self, attrs):
        qs = Team.objects.filter(project=attrs['project'])
        for project in qs:
            if project.name == attrs['name']:
                raise ValidationError('이미 존재하는 팀명입니다.')
        return super(TeamSerializer, self).validate(attrs)


class TeamUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


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


class AttachmentSerializer(serializers.ModelSerializer):
    filename = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = '__all__'

    def get_filename(self, obj):
        return obj.filename

    def to_representation(self, instance):
        result = super(AttachmentSerializer, self).to_representation(instance)
        try:
            author = User.objects.get(id=result['author'])
        except User.DoesNotExist:
            raise ValidationError('파일의 게시자가 존재하지 않습니다.')

        result['author'] = ProjectUserSerializer(author).data
        return result