import http

# from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings

from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.common.helpers import send_user_email
from apps.tasks.models import Task, Comment
from apps.tasks.serializers import TaskSerializer, TaskAssignSerializer, TaskCommentSerializer


class TaskViewSet(ModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    permission_classes = (IsAuthenticated,)
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['id', 'status']
    filter_backends = [filters.SearchFilter]
    search_fields = ['$title']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['PUT'], serializer_class=TaskAssignSerializer)
    def assign(self, request):
        Task.objects.filter(pk=self.request.data['id']).update(assigned_to=self.request.data['assigned_to'])
        task = Task.objects.get(pk=self.request.data['id'])
        send_user_email(
            subject="You have ben assigned a new task!",
            message=f"You have ben assigned a new task!\n The new task is \"{task.title}\".",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[request.user.email]
        )
        return Response({}, status=http.HTTPStatus.OK)

    def perform_update(self, serializer):
        super().perform_update(serializer)
        if serializer.instance.status == Task.Status.COMPLETED:
            comments = Comment.objects.filter(task=serializer.instance)
            for comment in comments:
                send_user_email(
                    subject="Your task, that was commented is completed!",
                    message=f"You have just executed a task!\n The completed task is \'{serializer.instance.title}\'.",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[comment.user.email]
                )


class CommentViewSet(ModelViewSet):
    serializer_class = TaskCommentSerializer
    queryset = Comment.objects.all()
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        headers = self.get_success_headers(serializer.data)
        task = Task.objects.get(pk=serializer.data['task'])
        send_user_email(
            subject='Your task got a new comment!',
            message=f'The task \"{task.title}\" got a new comment :\n {serializer.data["text"]}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[request.user.email]
        )
        return Response(serializer.data, status=201, headers=headers)
