from django.conf import settings

from rest_framework import serializers

from apps.common.helpers import send_user_email
from apps.tasks.models import Comment
from apps.tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ["owner"]

    def update(self, instance, validated_data):
        if validated_data["status"] == Task.Status.COMPLETED and instance.status != Task.Status.COMPLETED:
            comments = instance.comments.all()
            for comment in comments:
                send_user_email(
                    subject="Your task, that was commented is completed!",
                    message=f"You have just executed a task!\n The completed task is {instance.title}.",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[comment.owner.email]
                )
                
        return super().update(instance, validated_data)


class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("id", "title")


class TaskAssignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = (
            "title",
            "status",
            "owner",
            "description"
        )


class TaskCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = "__all__"
        extra_kwargs = {"owner": {"read_only": True}}
