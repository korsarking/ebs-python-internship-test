from django.contrib.auth import get_user_model
from drf_util.decorators import serialize_decorator
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.serializers import RegisterUsersSerializer, ListUsersSerializer

User = get_user_model()


class RegisterUserView(GenericAPIView):
    serializer_class = RegisterUsersSerializer
    queryset = User.objects.all()

    permission_classes = (AllowAny,)
    authentication_classes = ()

    @serialize_decorator(serializer_class)
    def post(self, request):
        validated_data = request.serializer.validated_data

        # Get password from validated data
        password = validated_data.pop("password")

        # Create user
        user = User.objects.create(
            **validated_data,
            is_superuser=True,
            is_staff=True,
        )

        # Set password
        user.set_password(password)
        user.save()

        refresh_token = RefreshToken().for_user(request.user)

        return Response({
            "refresh": str(refresh_token),
            "access": str(refresh_token.access_token)
        })


class ListUserViewSet(ListModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = ListUsersSerializer
    permission_classes = (IsAuthenticated,)
