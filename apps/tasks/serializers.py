from django.conf import settings
from django.core.mail import send_mail

from rest_framework import serializers

from apps.tasks.models import Comment
from apps.tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"
        extra_kwargs = {"owner": {"required": False}}

    def update(self, instance, validated_data):
        old_status = instance.status
        old_owner = instance.owner
        instance = super().update(instance, validated_data)
        new_status = instance.status
        new_owner = instance.owner

        if new_status == Task.Status.COMPLETED and old_status != Task.Status.COMPLETED:
            for comment in instance.comments.all():
                send_mail(
                    subject="Your task, that was commented is completed!",
                    message=f"You have just executed a task!\n The completed task is {instance.title}.",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[comment.owner.email]
                )

        if old_owner != new_owner:
            send_mail(
                subject="You have been assigned to a new task!",
                message=f"You have been assigned to a new task!\n The new task is \"{instance.title}\".",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[instance.owner.email]
            )

        return instance


class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("id", "title")


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"
        extra_kwargs = {"owner": {"read_only": True}}
