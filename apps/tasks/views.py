from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.tasks.models import Task
from apps.tasks.models import Comment
from apps.tasks.models import TimeLog
from apps.tasks.models import Timer
from apps.tasks.serializers import (
    TaskSerializer,
    TaskListSerializer,
    CommentSerializer,
    CommentListSerializer,
    TimelogSerializer,
    TimelogCreateSerializer,
    TimelogListSerializer,
    TimerSerializer,
    TimelogByMonthSerializer
)

from config.settings import CACHE_TTL


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    permission_classes = (IsAuthenticated,)
    filterset_fields = ["owner", "status"]
    search_fields = ["title"]
    ordering = ["-id"]

    def get_queryset(self):
        queryset = super().get_queryset()
        match self.action:
            case "top_month_duration":
                return Task.objects.total_duration()
            case _:
                return queryset

    def get_serializer_class(self):
        match self.action:
            case "list" | "top_month_duration":
                return TaskListSerializer
            case _:
                return TaskSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(methods=["POST"], detail=True)
    def start(self, request, pk=None, *args, **kwargs):
        instance, _ = Timer.objects.get_or_create(owner=self.request.user, task_id=pk)
        instance.start()
        return Response(TimerSerializer(instance).data)

    @action(methods=["POST"], detail=True)
    def stop(self, request, pk=None, *args, **kwargs):
        instance = get_object_or_404(Timer.objects.all(), owner=self.request.user, task_id=pk)
        instance.stop()
        return Response(TimelogSerializer(instance).data)

    @method_decorator(cache_page(CACHE_TTL))
    @action(methods=["GET"], detail=False)
    def top_month_duration(self, response, *args, **kwargs):
        tasks = self.get_queryset().order_by("-total_duration")[:20]

        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    permission_classes = (IsAuthenticated,)
    filterset_fields = ["task"]
    search_fields = ["text"]
    ordering = ["-id"]

    def get_serializer_class(self):
        match self.action:
            case "list":
                return CommentListSerializer
            case _:
                return CommentSerializer


class TimelogViewSet(ModelViewSet):
    queryset = TimeLog.objects.all()
    permission_classes = (IsAuthenticated,)
    filterset_fields = ["task"]
    ordering = ["-id"]

    def get_serializer_class(self):
        match self.action:
            case "list":
                return TimelogListSerializer
            case "create":
                return TimelogCreateSerializer
            case "last_month_full_time":
                return TimelogByMonthSerializer
            case _:
                return TimelogSerializer

    @action(methods=["GET"], detail=False)
    def last_month_full_time(self, request, *args, **kwargs):
        owner = self.request.user

        instance_duration = TimeLog.objects.last_month(owner=owner)
        serializer = self.get_serializer(data=instance_duration)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
