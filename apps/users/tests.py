from django.contrib.auth.hashers import make_password

from rest_framework.test import APITestCase
from rest_framework.status import HTTP_200_OK
from rest_framework.reverse import reverse

from apps.users.serializers import RegisterUsersSerializer
from apps.users.serializers import ListUsersSerializer
from apps.users.models import User
from apps.users.views import UserViewSet

from faker import Faker

faker = Faker()


class TestUsersCase(APITestCase):

    def setUp(self) -> None:
        full_name = faker.name()
        self.user = User.objects.create(
            first_name=full_name.split()[0],
            last_name=full_name.split()[1],
            email=faker.email(),
            password=make_password("StrongPassword"),
        )

        self.client.force_authenticate(user=self.user)

    def test_register_user(self):
        full_name = faker.name()
        data = {
            "first_name": full_name.split()[0],
            "last_name": full_name.split()[1],
            "email": faker.email(),
            "password": faker.password(),
        }

        response = self.client.post(reverse("user_register"), data=data)
        self.assertEqual(HTTP_200_OK, response.status_code)

    def test_serializer_class_for_register_action(self):
        view = UserViewSet()
        view.action = "register"
        serializer_class = view.get_serializer_class()
        self.assertEqual(serializer_class, RegisterUsersSerializer)

    def test_serializer_class_for_list_action(self):
        view = UserViewSet()
        view.action = "list"
        serializer_class = view.get_serializer_class()
        self.assertEqual(serializer_class, ListUsersSerializer)

    def test_login(self):
        data = {
            "email": self.user.email,
            "password": "StrongPassword"
        }

        response_login = self.client.post(reverse("token_obtain_pair"), data=data)

        self.assertEqual(HTTP_200_OK, response_login.status_code)

        self.token_access = response_login.data["access"]
        self.token_refresh = response_login.data["refresh"]

    def test_get_user(self):
        full_name = faker.name()
        user2 = User.objects.create(
            first_name=full_name.split()[0],
            last_name=full_name.split()[1],
            email=faker.email(),
            password=make_password("StrongPassword"),
        )

        response = self.client.get(reverse("users-list"))
        counted_users = User.objects.count()

        self.assertEqual(HTTP_200_OK, response.status_code)
        self.assertContains(response, self.user.first_name)
        self.assertContains(response, user2.first_name)
        self.assertEqual(response.data.get("count"), counted_users)
