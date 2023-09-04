from rest_framework import serializers

from apps.tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"
        extra_kwargs = {
            "user": {"read_only": True}
        }


class DisplayTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("id", "title")


class TaskAssignSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Task
        fields = ["id", "user"]
