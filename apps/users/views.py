from django.contrib.auth import get_user_model

from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.viewsets import GenericViewSet

from apps.users.serializers import UserListSerializer
from apps.users.serializers import UserRegisterSerializer

User = get_user_model()


class UserViewSet(ListModelMixin, GenericViewSet):
    queryset = User.objects.all()
    search_fields = ["first_name"]
    ordering = ["id"]

    def get_permissions(self):
        match self.action:
            case "register":
                self.permission_classes = [AllowAny, ]
            case _:
                self.permission_classes = [IsAuthenticated, ]

        return super(UserViewSet, self).get_permissions()

    def get_serializer_class(self):
        match self.action:
            case "register":
                return UserRegisterSerializer
            case "list":
                return UserListSerializer

    @action(detail=False, methods=["POST"])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        password = validated_data.pop("password")

        user = serializer.save(**validated_data, is_superuser=True, is_staff=True)

        user.set_password(password)
        user.save()

        refresh_token = RefreshToken().for_user(request.user)

        return Response({
            "refresh": str(refresh_token),
            "access": str(refresh_token.access_token)
        })
