from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from issue.models import Project


class ProjectTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create(
            email='test@test.co',
            password='test',
            username='test'
        )
        cls.client = APIClient()

    def login(self, user):
        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    def logout(self):
        self.client.credentials()

    def test_로그인된유저는_프로젝트를_생성할수있다(self):
        data = {
            'name': 'project1',
            'key': 'P1',
            'leader': self.user.pk,
            'users': [self.user.pk]
        }
        res = self.client.post(f'/projects/', data);
        self.assertEqual(res.status_code, 401);

        self.login(self.user)
        res = self.client.post(f'/projects/', data);
        self.assertEqual(res.status_code, 201);
