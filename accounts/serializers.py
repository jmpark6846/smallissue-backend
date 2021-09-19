from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from accounts.models import User


class SITokenObtainSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        user_data = UserDetailSerializer(user).data
        token['user'] = user_data
        return token


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'email', 'username', 'is_staff', 'is_active']

