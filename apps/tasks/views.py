from django.conf import settings
from django.core.mail import send_mail
from rest_framework.viewsets import ModelViewSet

from apps.tasks.models import Comment
from apps.tasks.models import Task
from apps.tasks.serializers import TaskSerializer
from apps.tasks.serializers import TaskListSerializer
from apps.tasks.serializers import CommentSerializer


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filterset_fields = ["owner", "status"]
    search_fields = ["title"]
    ordering = ["-id"]

    def get_serializer_class(self):
        if self.action in ["list"]:
            return TaskListSerializer

        return TaskSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    filterset_fields = ["task"]
    search_fields = ["text"]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

        send_mail(
            subject="Your task got a new comment!",
            message=f"The task \"{serializer.validated_data.get('task').title}\""
                    f" got a new comment :\n {serializer.data.get('text')}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[serializer.validated_data.get("task").owner.email]
        )
