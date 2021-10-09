from django.urls import path

from accounts.views import get_unread_notifications, mark_as_read, mark_all_as_read

urlpatterns = [
    path('notifications/unread/', get_unread_notifications),
    path('notifications/mark_as_read/<pk>/', mark_as_read),
    path('notifications/mark_all_as_read/', mark_all_as_read)
]
