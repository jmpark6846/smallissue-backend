import os
import requests

from django.http.response import JsonResponse
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.kakao.provider import KakaoProvider
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User

KAKAO_API_KEY = os.getenv('KAKAO_API_KEY')

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    callback_url = "http://localhost:8000/accounts/google/login/callback/"


@api_view(['POST'])
def kakao_login(request):
    code = request.data.get('code')
    error = request.data.get('error')

    if error:
        error_desc = request.GET.get('error_description')
        return JsonResponse({'error': f'failed to get authorization code. {error_desc}'}, status=400)

    data = {
        'grant_type': 'authorization_code',
        'client_id': KAKAO_API_KEY,
        'code': code
    }
    res = requests.post('https://kauth.kakao.com/oauth/token', data=data)

    if res.status_code != 200:
        return JsonResponse({'error': 'failed to get access token'}, status=400)

    access_token = res.json().get('access_token')
    headers = {
        'Authorization': f'Bearer {access_token}',
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    params = {'property_keys': '["kakao_account.email"]'}
    res = requests.post('https://kapi.kakao.com/v2/user/me', data=params, headers=headers)

    if res.status_code != 200:
        return JsonResponse({'error': 'failed to get kakao account email. '}, status=400)

    email = res.json()['kakao_account']['email']
    user_id = res.json()['id']

    user, created = User.objects.get_or_create(
        email=email
    )

    if not created:
        social_account = SocialAccount.objects.get(user=user)
        if social_account.provider != KakaoProvider.id:
            return JsonResponse({'error': 'failed to login. try other login methods.'}, status=400)

        if not user.is_active:
            return JsonResponse({'error': 'deactivated user'}, status=400)
    else:
        SocialAccount.objects.create(
            user=user,
            provider=KakaoProvider.id,
            uid=user_id
        )

    refresh_token: RefreshToken = RefreshToken.for_user(user)
    res_data = {
        'refresh_token': str(refresh_token),
        'access_token': str(refresh_token.access_token)
    }
    return JsonResponse(res_data)

