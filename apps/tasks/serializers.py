from django.conf import settings

from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination

from apps.common.helpers import send_user_email
from apps.tasks.models import Task, Comment


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = '__all__'
        extra_kwargs = {
            "user": {"read_only": True},
            "assigned_to": {"read_only": True}
        }
        write_only_fields = [
            'id',
            'assigned_to',
        ]

    def update(self, instance, validated_data):
        if validated_data["status"] == Task.Status.COMPLETED and instance.status != Task.Status.COMPLETED:
            comments = instance.task_of_comment.all()
            for comment in comments:
                send_user_email(
                    subject="Your task, that was commented is completed!",
                    message=f"You have just executed a task!\n The completed task is \'{instance.title}\'.",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[comment.user.email]
                )
                
        return super().update(instance, validated_data)


class TaskCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"
        extra_kwargs = {
            "user": {"read_only": True}
        }


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500
