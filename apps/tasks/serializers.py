from django.conf import settings

from rest_framework import serializers
from rest_framework.decorators import action

from apps.common.helpers import send_user_email
from apps.tasks.models import Task, Comment


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"
        extra_kwargs = {
            "user": {"read_only": True},
            "assigned_to": {"read_only": True}
        }

    def update(self, instance, validated_data):
        if validated_data["status"] == Task.Status.COMPLETED and instance.status != Task.Status.COMPLETED:
            comments = Comment.objects.filter(task=instance)
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

