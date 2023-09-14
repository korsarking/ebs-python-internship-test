from rest_framework.routers import DefaultRouter
from apps.tasks.views import TaskViewSet, CommentViewSet

router = DefaultRouter(trailing_slash=False)

router.register(
    r'tasks/comments',
    CommentViewSet,
    basename='comments'
)

router.register(
    r'tasks',
    TaskViewSet,
    basename='tasks'
)

urlpatterns = router.urls
