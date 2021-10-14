from django.contrib.auth import get_user_model
from rest_framework.views import APIView

User = get_user_model()


class DjangoGroupCompatibleAPIView(APIView):
    queryset = User.objects.none()


#
# def django_group_compatible(view_func):
#     def wrap(request, *args, **kwargs):
#         func.queryset = User.objects.none()
#         return func
#
#     return decorator
