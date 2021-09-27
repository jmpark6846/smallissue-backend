from django.contrib.auth import get_user_model
from rest_framework import serializers
from issue.models import Project


class ProjectSerializer(serializers.ModelSerializer):
    # key = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'

    def validate(self, data):
        user = data['leader']
        if user.projects.filter(key=data['key']).exists():
            raise serializers.ValidationError('key not available')

        return data
