from rest_framework.routers import DefaultRouter
from apps.tasks.views import TaskViewSet, CommentViewSet


router = DefaultRouter(trailing_slash=False)
router.register(r'task', TaskViewSet, basename='task')
router.register(r'comments', CommentViewSet, basename='comments')
urlpatterns = router.urls
