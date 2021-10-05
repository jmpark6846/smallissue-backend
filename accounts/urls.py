from django.urls import path, include

from accounts.views import get_unread_notifications

urlpatterns = [
    path('notifications/unread/', get_unread_notifications)
]
