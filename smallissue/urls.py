"""smallissue URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import notifications.urls
from django.contrib import admin
from django.urls import path, include

from accounts.views import LogoutView
from issue.urls import urlpatterns as issue_urls

urlpatterns = [
   path('admin/', admin.site.urls),
   path('inbox/notifications/', include(notifications.urls, namespace='notifications')),
   path('accounts/', include('accounts.urls')),
   path('accounts/logout/', LogoutView.as_view(), name='logout'),

   # auth
   path('allauth/', include('allauth.urls')),
   path('accounts/', include('dj_rest_auth.urls')),
   path('accounts/registration/', include('dj_rest_auth.registration.urls')),

   # social login
   # path('accounts/google/login/', GoogleLogin.as_view(), name="google_login"),
   # path('accounts/kakao/login/', kakao_login, name='kakao_login'),
] + issue_urls