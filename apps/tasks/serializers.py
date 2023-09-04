from rest_framework import serializers

from apps.tasks.models import Task, Comment


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"
        extra_kwargs = {
            "user": {"read_only": True},
            "assigned_to": {"read_only": True}
        }


class DisplayTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("id", "title")


class TaskAssignSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    assigned_to = serializers.IntegerField()

    class Meta:
        model = Task
        fields = ('id', 'assigned_to')


class TaskCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id',
            'task',
            'text',
        ]


class CommentCompletedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['task']
