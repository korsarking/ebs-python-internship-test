from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter

from apps.users.views import UserViewSet

router = DefaultRouter(trailing_slash=False)
router.register(
    r"users",
    UserViewSet,
    basename="users"
)

urlpatterns = [
    path(
        r"users/login",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair"
    ),
    path(
        r"users/token-refresh",
        TokenRefreshView.as_view(),
        name="token_refresh"
    ),
]

urlpatterns += router.urls
