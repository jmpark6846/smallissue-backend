from django.urls import path

from accounts.views import get_unread_notifications, mark_as_read, mark_all_as_read, search_user_by_email, ProfileView, \
    UnreadNotificiationAPIView, MarkAsReadAPIView, MarkAllAsReadAPIView, SearchUserByEmailAPIView

urlpatterns = [
    path('notifications/unread/', UnreadNotificiationAPIView.as_view()),
    path('notifications/mark_as_read/<pk>/', MarkAsReadAPIView.as_view()),
    path('notifications/mark_all_as_read/', MarkAllAsReadAPIView.as_view()),
    path('search/', SearchUserByEmailAPIView.as_view()),
    path('profile/', ProfileView.as_view()),
]
