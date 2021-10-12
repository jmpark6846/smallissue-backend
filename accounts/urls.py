from django.urls import path

from accounts.views import get_unread_notifications, mark_as_read, mark_all_as_read, search_user_by_email, ProfileView

urlpatterns = [
    path('notifications/unread/', get_unread_notifications),
    path('notifications/mark_as_read/<pk>/', mark_as_read),
    path('notifications/mark_all_as_read/', mark_all_as_read),
    path('search/', search_user_by_email),
    path('profile/', ProfileView.as_view()),
]
