from rest_framework.routers import DefaultRouter

from apps.tasks.views import CommentViewSet
from apps.tasks.views import TaskViewSet
from apps.tasks.views import TimelogViewSet

router = DefaultRouter(trailing_slash=False)

router.register(
    r"tasks/comments",
    CommentViewSet,
    basename="comments"
)

router.register(
    r"tasks/timelog",
    TimelogViewSet,
    basename="timelog"
)

router.register(
    r"tasks",
    TaskViewSet,
    basename="tasks"
)

urlpatterns = router.urls
