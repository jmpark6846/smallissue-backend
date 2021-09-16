from django.conf import settings
from rest_framework.test import APITestCase, APIClient
from accounts.models import User


class UserTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        data = {
            'email': 'test@test.com',
            'username': 'test',
            'password1': 'test12#$',
            'password2': 'test12#$',
        }
        cls.data = data
        cls.test_user = User.objects.create(
            email="test2@test.com",
            username="test2",
        )
        cls.test_user.set_password('test12#$')
        cls.test_user.save()

    def test_회원가입하면_유저와_함께_유저의_프로필_생성(self):
        response = self.client.post('/accounts/registration/', data=self.data)
        email = response.data['user']['email']
        user = User.objects.get(email=email)
        self.assertIsNotNone(user.profile)

