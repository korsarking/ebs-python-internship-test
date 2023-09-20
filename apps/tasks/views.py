from django.conf import settings
from django.shortcuts import get_object_or_404

from drf_yasg.utils import swagger_auto_schema

from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.common.helpers import send_user_email
from apps.tasks.models import Comment
from apps.tasks.models import Task
from apps.users.models import User
from apps.tasks.serializers import (
    TaskSerializer, TaskListSerializer, TaskCommentSerializer,
    TaskAssignSerializer
)


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filterset_fields = ["owner_id", "status"]
    search_fields = ["title"]
    ordering = ["-id"]

    def get_serializer_class(self):
        if self.action in ["list"]:
            return TaskListSerializer
        if self.action in ["assign"]:
            return TaskAssignSerializer
        return TaskSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @swagger_auto_schema(responses={HTTP_204_NO_CONTENT: ""}, request=None)
    @action(detail=True, methods=["PATCH"], url_path=r"assign/(?P<owner>\d+)")
    def assign(self, request, pk, owner):
        instance = self.get_object()
        instance.status = Task.Status.ASSIGNED
        instance.owner = get_object_or_404(User, pk=owner)
        instance.save(update_fields=["owner", "status"])

        send_user_email(
            subject="You have been assigned to a new task!",
            message=f"You have been assigned to a new task!\n The new task is \"{instance.title}\".",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[instance.owner.email]
        )
        return Response(status=HTTP_204_NO_CONTENT)


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = TaskCommentSerializer
    filterset_fields = ["task"]
    search_fields = ["text"]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

        send_user_email(
            subject="Your task got a new comment!",
            message=f'The task \"{serializer.validated_data.get("task").title}\"'
                    f' got a new comment :\n {serializer.data.get("text")}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[serializer.validated_data.get("task").owner.email]
        )
