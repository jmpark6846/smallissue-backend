import os
from django.utils.translation import gettext_lazy as _

import requests
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from dj_rest_auth.jwt_auth import unset_jwt_cookies

from django.http.response import JsonResponse
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.kakao.provider import KakaoProvider
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from dj_rest_auth.views import LogoutView as dj_rest_auth_LogoutView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User
from accounts.serializers import NotificationSerializer

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


@api_view(['GET'])
def get_unread_notifications(request: Request):
    if not request.user:
        return Response(status=401)

    unread_list = request.user.notifications.unread()

    return Response({
        "unread_count": len(unread_list),
        "unread_list": NotificationSerializer(unread_list, many=True).data
    }, status=200)


class LogoutView(dj_rest_auth_LogoutView):
    def logout(self, request: Request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            pass

        response = Response(
            {'detail': 'Successfully logged out.'},
            status=status.HTTP_200_OK,
        )
        try:
            refresh = request.COOKIES['refresh']
        except KeyError:
            response.data = {'detail': _('Refresh token was not included in cookie.')}
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return response

        unset_jwt_cookies(response)

        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except (TokenError, AttributeError, TypeError) as error:
            if hasattr(error, 'args'):
                if 'Token is blacklisted' in error.args or 'Token is invalid or expired' in error.args:
                    response.data = {'detail': _(error.args[0])}
                    response.status_code = status.HTTP_401_UNAUTHORIZED
                else:
                    response.data = {'detail': _('An error has occurred.')}
                    response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

            else:
                response.data = {'detail': _('An error has occurred.')}
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        return response

