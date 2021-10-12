
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator

from rest_framework import status
from rest_framework.decorators import api_view, action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from issue.models import Project, Issue, Tag, IssueTagging, IssueHistory, Participation, Team
from issue.pagination import DefaultPagination
from issue.permissions import ProjectUsersOnly, ProjectLeaderOnly, IsAuthorOnly
from issue.serializers import ProjectSerializer, IssueSerializer, ProjectUserSerializer, IssueDetailSerializer, \
    CommentSerializer, TagSerializer, TeamSerializer, ProjectParticipationSerializer, TeamUserSerializer
from smallissue.utils import get_or_none_if_pk_is_none

User = get_user_model()


class ProjectViewSet(ModelViewSet):
    serializer_class = ProjectSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'users', 'teams']:
            permission_classes = [ProjectUsersOnly, IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action in ['destroy', 'update', 'set_orders']:
            permission_classes = [ProjectLeaderOnly, IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return self.request.user.projects.order_by('order')

    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        project = self.get_object()
        users = ProjectUserSerializer(project.users, many=True).data
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


class ProjectParticipationViewSet(ModelViewSet):
    serializer_class = ProjectParticipationSerializer
    pagination_class = DefaultPagination

    def get_permissions(self):
        if self.action in ['destroy']:
            permission_classes = [ProjectLeaderOnly, IsAuthenticated]
        else:
            permission_classes = [ProjectUsersOnly, IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return Participation.objects.filter(project=self.kwargs['project_pk']).order_by('-date_joined')

    def create(self, request, *args, **kwargs):
        try:
            project = Project.objects.get(id=self.kwargs['project_pk'])
        except Project.DoesNotExist:
            return Response('프로젝트가 존재하지 않습니다.', status=404)

        user_id = request.data['user']
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response('추가하려는 사용자가 존재하지 않습니다.', status=404)

        p = Participation.objects.filter(project=project, user=user).last()

        if p:
            return Response(ProjectParticipationSerializer(p).data, status.HTTP_302_FOUND)

        p = Participation.objects.create(
            project=project,
            user=user
        )
        return Response(ProjectParticipationSerializer(p).data, status=status.HTTP_201_CREATED)


class ProjectTeamViewSet(ModelViewSet):
    serializer_class = TeamSerializer
    permission_classes = [ProjectUsersOnly, IsAuthenticated]
    pagination_class = DefaultPagination

    def get_queryset(self):
        return Team.objects.filter(project=self.kwargs['project_pk']).order_by('name')


class ProjectTeamUsersViewSet(ModelViewSet):
    serializer_class = TeamUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(project_teams__id=self.kwargs['team_pk'])

    def create(self, request, *args, **kwargs):
        user_id = self.request.data.get('user')
        try:
            user = User.objects.get(id=user_id)
            team = Team.objects.get(id=self.kwargs['team_pk'])
        except User.DoesNotExist:
            return Response('추가하려는 사용자가 존재하지 않습니다.', status=404)
        except Team.DoesNotExist:
            return Response('추가하려는 팀이 존재하지 않습니다.', status=404)

        team.users.add(user)
        return Response(TeamUserSerializer(team.users, many=True).data)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        try:
            team = Team.objects.get(id=self.kwargs['team_pk'])
        except Team.DoesNotExist:
            return Response('추가하려는 팀이 존재하지 않습니다.', status=404)

        team.users.remove(user)
        return Response(TeamUserSerializer(team.users, many=True).data)


class ProjectIssueViewSet(ModelViewSet):
    permission_classes = [ProjectUsersOnly, IsAuthenticated]
    HISTORY_PAGINATION_SIZE = 10

    def get_queryset(self):
        return Issue.objects.filter(project=self.kwargs['project_pk'], deleted_at=None).order_by('order')

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update']:
            return IssueDetailSerializer
        return IssueSerializer

    @action(detail=True, methods=['patch'])
    def toggle_subscription(self, request, **kwargs):
        issue = self.get_object()
        if request.user in issue.subscribers.all():
            issue.subscribers.remove(request.user)
        else:
            issue.subscribers.add(request.user)

        subs = list(map(lambda x: x.pk, issue.subscribers.all()))
        return Response(data={'subscribers': subs}, status=200)

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

            else:
                deleted = issue.tags.exclude(name__in=tag_name_inputs).all()
                for tag in deleted:
                    IssueTagging.objects.get(
                        issue=issue,
                        tag=tag
                    ).delete()

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
        histories = IssueHistory.objects.filter(issue_id=issue.id)
        paginator = Paginator(histories, self.HISTORY_PAGINATION_SIZE)
        history_page_num = request.GET.get('history_page')
        page_obj = paginator.get_page(history_page_num)

        for issue_history in page_obj.object_list:
            h = issue_history.history

            if h.__class__ == Issue.history.model:
                if h.prev_record:
                    delta = h.diff_against(h.prev_record, excluded_fields=['order', 'project', ])
                    for change in delta.changes:
                        if change.field == 'key':
                            continue

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
            elif h.__class__ == IssueTagging.history.model:
                result.append({
                    'field': 'tags',
                    'old_value': None,
                    'new_value': h.tag.name,
                    'user': {'id': h.history_user.id, 'username': h.history_user.username},
                    'type': h.history_type,
                    'date': h.history_date
                })
            else:
                raise TypeError('이슈와 이슈태깅 히스토리컬 모델이 아닙니다.')

        return Response(data={'list': result, 'count': len(result), 'page_size': self.HISTORY_PAGINATION_SIZE,
                              'current_page': page_obj.number}, status=200)


class ProjectCommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = DefaultPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [ProjectUsersOnly, IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [ProjectUsersOnly, IsAuthenticated]
        elif self.action in ['destroy', 'update', 'partial_update']:
            permission_classes = [IsAuthorOnly, IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return Issue.objects.get(id=self.kwargs['issue_pk'], deleted_at=None).comments.filter(deleted_at=None).order_by(
            '-created_at')
