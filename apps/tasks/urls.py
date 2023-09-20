from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.tasks.views import CommentViewSet
from apps.tasks.views import TaskViewSet

router = DefaultRouter(trailing_slash=False)

router.register(
    r"tasks/comments",
    CommentViewSet,
    basename="comments"
)

router.register(
    r"tasks",
    TaskViewSet,
    basename="tasks"
)

urlpatterns = [
    path("tasks/<int:id>/assign/<int:assigned_to>/", TaskViewSet, name="tasks-assign")
]

urlpatterns += router.urls
