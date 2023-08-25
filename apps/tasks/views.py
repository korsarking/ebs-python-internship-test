from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.tasks.models import Task
from apps.tasks.serializers import TaskSerializer, TaskAssignSerializer, DisplayTaskSerializer


class TaskViewSet(ModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    permission_classes = (IsAuthenticated,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['=id']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, serializer_class=DisplayTaskSerializer)
    def display_my(self, request, *args, **kwargs):
        instance = Task.objects.filter(user=self.request.user)
        serializer = DisplayTaskSerializer(instance, many=True)
        return Response(data=serializer.data)

    @action(detail=False, serializer_class=TaskSerializer)
    def completed(self, request, *args, **kwargs):
        complete_task = Task.objects.filter(status="Completed")
        serializer = TaskSerializer(complete_task, many=True)
        return Response(data=serializer.data)

    @action(methods=["PATCH"], detail=False, serializer_class=TaskAssignSerializer)
    def assign(self, request, *args, **kwargs):
        Task.objects.filter(pk=self.request.data["id"]).update(user=self.request.data["user"])
        return Response(status.HTTP_200_OK)
