from itertools import chain

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Model
from django.forms.models import model_to_dict
from django.shortcuts import render
from django.core.paginator import Paginator

from rest_framework import status
from rest_framework.decorators import api_view, action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from issue.models import Project, Issue, Tag, IssueTagging
from issue.pagination import CommentPagination
from issue.permissions import ProjectTeammateOnly, ProjectLeaderOnly, IsAuthorOnly
from issue.serializers import ProjectSerializer, IssueSerializer, ProjectUserSerializer, IssueDetailSerializer, \
    ProjectAssigneeListSerializer, CommentSerializer, TagSerializer


class ProjectViewSet(ModelViewSet):
    serializer_class = ProjectSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'users']:
            permission_classes = [ProjectTeammateOnly, IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action in ['destroy', 'update', 'set_orders']:
            permission_classes = [ProjectLeaderOnly, IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return self.request.user.projects.order_by('order')

    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        project = self.get_object()
        users = ProjectAssigneeListSerializer(project.users, many=True).data
        return Response({'users': users})

    @action(detail=False, methods=['patch'])
    def set_orders(self, request, **kwargs):
        projects = self.get_queryset()
        new_orders = {}
        for i, id in enumerate(request.data.get('new_orders')):
            new_orders[int(id)] = i

        for project in projects:
            project.order = new_orders[project.id]
            project.save()

        return Response(status=200)


@api_view(['GET'])
def check_project_key_available(request: Request):
    key = request.query_params.get('key')

    if not isinstance(key, str):
        return Response(data={'available': False, 'error_msg': '문자가 아닙니다.'})

    import string
    key = key.upper()
    if not key.isascii() or not key[0] in string.ascii_uppercase:
        return Response(data={'available': False, 'error_msg': '영문자, 숫자, 특수문자만 사용할 수 있으며 첫 문자는 영문자여야 합니다.'})

    if request.user.projects.filter(key=key).exists():
        return Response(data={'available': False, 'error_msg': '프로젝트에서 이미 사용하고 있는 키값입니다.'})

    return Response(data={'available': True})


def get_or_none_if_pk_is_none(model: Model, pk):
    if pk is None:
        return None

    return model.objects.get(pk=pk)


def get_fields_from_model(model):
    model_field_names = list(set(chain.from_iterable(
        (field.name, field.attname) if hasattr(field, 'attname') else (field.name,)
        for field in model._meta.get_fields()
        # For complete backwards compatibility, you may want to exclude
        # GenericForeignKey from the results.
        if not (field.many_to_one and field.related_model is None)
    )))
    return model_field_names

#
# def create_historical_record_manually(instance, history_dict):
#     model = type(instance)
#     model_field_names = get_fields_from_model(model)
#     history_model = model.history.model
#
#     model_attr_dict = {
#
#     }
#
#     for field_name in model_field_names:
#
#
#     new_historical_record = model.objects.create(
#         **
#     )
#
#     history_dict = dict(
#         history_user = self.request.user,
#         history_date = timezone.now(),
#         history_change_reason = '',
#         history_type = '~',
#
#     )

class ProjectIssueViewSet(ModelViewSet):
    permission_classes = [ProjectTeammateOnly, IsAuthenticated]
    HISTORY_PAGINATION_SIZE = 10

    def get_queryset(self):
        return Issue.objects.filter(project=self.kwargs['project_pk'], deleted_at=None).order_by('order')

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update']:
            return IssueDetailSerializer
        return IssueSerializer

    @action(detail=False, methods=['patch'])
    def set_orders(self, request, **kwargs):
        issues = self.get_queryset()
        new_orders = {}
        for i, id in enumerate(request.data.get('new_orders')):
            new_orders[int(id)] = i

        for issue in issues:
            issue.order = new_orders[issue.id]
            issue.save()

        return Response(status=200)

    @action(detail=True, methods=['GET', 'POST'])
    def tags(self, request: Request, **kwargs):
        if request.method == 'POST':
            issue = self.get_object()
            tag_name_inputs: list = request.data.get('tags')
            is_adding_tag = len(tag_name_inputs) > issue.tags.count()

            if is_adding_tag:
                for tag_input in tag_name_inputs:
                    if not issue.tags.filter(name=tag_input).exists():
                        tag = Tag.objects.create(
                            name=tag_input,
                        )
                        IssueTagging.objects.create(
                            tag=tag,
                            issue=issue,
                        )

                        # tag.issues.add(issue)
            else:
                deleted = issue.tags.exclude(name__in=tag_name_inputs).all()
                for tag in deleted:
                    IssueTagging.objects.get(
                        issue=issue,
                        tag=tag
                    ).delete()
                    # issue.tags.remove(tag)

            tag_names = []
            qs = issue.tags.all()
            for tag in qs:
                tag_names.append(tag.name)
            return Response(data={'tags': tag_names}, status=200)
        else:
            issue = self.get_object()
            tag_names = []
            qs = issue.tags.all()
            for tag in qs:
                tag_names.append(tag.name)
            return Response(data={'tags': tag_names}, status=200)

    @action(detail=True, methods=['GET'])
    def history(self, request, **kwargs):
        User = get_user_model()
        issue = self.get_object()
        result = []
        histories = issue.history.order_by('-history_date')
        tag_histories = IssueTagging.history.filter(issue=issue).order_by('-history_date')
        paginator = Paginator(histories, self.HISTORY_PAGINATION_SIZE)
        history_page_num = request.GET.get('history_page')
        page_obj = paginator.get_page(history_page_num)

        for h in page_obj.object_list:
            if h.prev_record:
                delta = h.diff_against(h.prev_record, excluded_fields=['order', 'project', ])
                for change in delta.changes:
                    data = {
                        'field': change.field,
                        'user': {'id': h.history_user.id, 'username': h.history_user.username},
                        'type': h.history_type,
                        'date': h.history_date,
                    }
                    if change.field == 'assignee':
                        old_assignee = get_or_none_if_pk_is_none(User, change.old)
                        new_assignee = get_or_none_if_pk_is_none(User, change.new)
                        data['old_value'] = {'id': change.old,
                                             'username': old_assignee.username if old_assignee else None}
                        data['new_value'] = {'id': change.new,
                                             'username': new_assignee.username if new_assignee else None}
                    else:
                        data['old_value'] = change.old
                        data['new_value'] = change.new

                    result.append(data)

            else:
                result.append({
                    'field': None,
                    'old_value': None,
                    'new_value': None,
                    'user': {'id': h.history_user.id, 'username': h.history_user.username},
                    'type': h.history_type,
                    'date': h.history_date,
                })

        return Response(data={'list': result, 'count': histories.count(), 'page_size': self.HISTORY_PAGINATION_SIZE,
                              'current_page': page_obj.number}, status=200)


class ProjectCommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = CommentPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [ProjectTeammateOnly, IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [ProjectTeammateOnly, IsAuthenticated]
        elif self.action in ['destroy', 'update', 'partial_update']:
            permission_classes = [IsAuthorOnly, IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return Issue.objects.get(id=self.kwargs['issue_pk'], deleted_at=None).comments.filter(deleted_at=None).order_by(
            '-created_at')

#
#
# @api_view(['GET'])
# def get_or_create_tags(request):
#     if request.method == 'GET':
#         tag_name = request.GET.get('tag')
#
#         tag = Tag.objects.get_or_create(
#             tag_name = tag_name,
#             issue=
#         )
#     else:
#         return Response(status=405)
