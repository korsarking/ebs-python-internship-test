from datetime import datetime, timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils.timezone import utc

from rest_framework import serializers

from apps.users.serializers import UserSerializer
from apps.tasks.models import Task
from apps.tasks.models import Comment
from apps.tasks.models import TimeLog
from apps.tasks.models import Timer


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
    total_duration = serializers.DurationField(read_only=True)
    owner = UserSerializer()

    class Meta:
        model = Task
        fields = "__all__"
        extra_kwargs = {
            "created_at": {"required": False},
            "updated_at": {"required": False}
        }


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"
        extra_kwargs = {"owner": {"read_only": True}}

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        instance = super().create(validated_data)
        send_mail(
            subject="Your task got a new comment!",
            message=f"The task \"{validated_data.get('task').title}\""
                    f" got a new comment :\n {self.data.get('text')}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[validated_data.get("task").owner.email]
        )

        return instance


class CommentListSerializer(serializers.ModelSerializer):
    owner = UserSerializer()
    task = TaskSerializer()

    class Meta:
        model = Comment
        fields = "__all__"


class TimelogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeLog
        fields = "__all__"
        read_only_fields = [
            "created_by",
            "status",
            "assigned_to",
        ]


class TimelogCreateSerializer(serializers.ModelSerializer):
    date_field = serializers.DateField(write_only=True)
    duration_minutes = serializers.IntegerField(write_only=True)

    class Meta:
        model = TimeLog
        fields = "__all__"
        read_only_fields = [
            "started_at",
            "duration",
            "owner",
        ]

    def create(self, validated_data):
        timelog = TimeLog.objects.create(
            task=validated_data["task"],
            owner=self.context["request"].user,
            duration=timedelta(minutes=validated_data["duration_minutes"]),
            started_at=datetime.combine(
                validated_data["date_field"], datetime.min.time()
            ).replace(tzinfo=utc)
        )

        return timelog


class TimelogListSerializer(serializers.ModelSerializer):
    owner = UserSerializer()
    task = TaskSerializer()

    class Meta:
        model = TimeLog
        fields = "__all__"


class TimelogByMonthSerializer(serializers.ModelSerializer):
    total = serializers.DurationField(allow_null=True)

    class Meta:
        model = TimeLog
        fields = ("total",)


class TimerSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    task = TaskSerializer(read_only=True)

    class Meta:
        model = Timer
        fields = "__all__"
