from django.conf import settings
from django.shortcuts import get_object_or_404

from drf_yasg.utils import swagger_auto_schema

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.common.helpers import send_user_email
from apps.tasks.models import Task, Comment
from apps.tasks.serializers import (TaskSerializer, TaskCommentSerializer, StandardResultsSetPagination)
from apps.users.models import User


class TaskViewSet(ModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.all().order_by('id')
    permission_classes = (IsAuthenticated,)
    pagination_class = StandardResultsSetPagination
    filterset_fields = ['user_id', 'title', 'status']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['POST'])
    def complete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != Task.Status.COMPLETED:
            instance.status = Task.Status.COMPLETED
            instance.save()
            send_user_email(
                subject="Completed task!",
                message=f"Your task:\"{instance.title}\" is completed now.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[request.user.email]
            )
        serializer = self.get_serializer(instance=instance)
        return Response(serializer.data)

    @swagger_auto_schema(responses={204: ""}, request=None)
    @action(detail=True, methods=['PATCH'], url_path=r"reassign/(?P<assigned_to>\d+)",
            serializer_class=None)
    def assign(self, request, pk, assigned_to):
        instance = self.get_object()
        instance.status = Task.Status.ASSIGNED
        instance.assigned_to = get_object_or_404(User, pk=assigned_to)
        instance.save(update_fields=["assigned_to", "status"])

        send_user_email(
            subject="You have ben assigned a new task!",
            message=f"You have ben assigned a new task!\n The new task is \"{instance.title}\".",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[instance.assigned_to.email]
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(ModelViewSet):
    serializer_class = TaskCommentSerializer
    queryset = Comment.objects.all()
    permission_classes = (IsAuthenticated,)
    pagination_class = StandardResultsSetPagination
    filterset_fields = ['task']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

        send_user_email(
            subject='Your task got a new comment!',
            message=f'The task \"{serializer.validated_data.get("task").title}\"'
                    f' got a new comment :\n {serializer.data.get("text")}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[serializer.validated_data.get("task").user.email]
        )
