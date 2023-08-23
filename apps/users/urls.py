from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from rest_framework.routers import DefaultRouter

from apps.users.views import RegisterUserView
from apps.users.views import ListUserViewSet

router = DefaultRouter()
router.register(r'users', ListUserViewSet)

urlpatterns = [
    path("register", RegisterUserView.as_view(), name="token_register"),
    path("token", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
]

urlpatterns += router.urls
