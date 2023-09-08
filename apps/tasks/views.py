import django_filters
from django.conf import settings
from django.shortcuts import get_object_or_404

from drf_yasg.utils import swagger_auto_schema

from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.common.helpers import send_user_email
from apps.tasks.models import Task, Comment
from apps.users.models import User
from apps.tasks.serializers import TaskSerializer, TaskCommentSerializer


class TaskViewSet(ModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    permission_classes = (IsAuthenticated,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['$title']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(responses={204: ""}, request=None)
    @action(detail=True, methods=['PUT'], url_path=r"reassign/(?P<assigned_to>\d+)",
            serializer_class=None)
    def assign(self, request, pk, assigned_to):
        instance = self.get_object()
        instance.assigned_to = get_object_or_404(User, pk=assigned_to)
        instance.save(update_fields=["assigned_to"])

        send_user_email(
            subject="You have ben assigned a new task!",
            message=f"You have ben assigned a new task!\n The new task is \"{instance.title}\".",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[request.user.email]
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(ModelViewSet):
    serializer_class = TaskCommentSerializer
    queryset = Comment.objects.all()
    permission_classes = (IsAuthenticated,)
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['task']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

        send_user_email(
            subject='Your task got a new comment!',
            message=f'The task \"{serializer.validated_data.get("task").title}\"'
                    f' got a new comment :\n {serializer.data.get("text")}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[self.request.user.email]
        )
