from django.contrib.auth.hashers import make_password
from faker import Faker
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK
from rest_framework.test import APITestCase

from apps.users.models import User

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
        data = {
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "email": faker.email(),
            "password": faker.password(),
        }

        response = self.client.post(reverse("user_register"), data=data)
        self.assertEqual(HTTP_200_OK, response.status_code)

        user = User.objects.get(email=data["email"])

        self.assertEqual(user.email, data["email"])
        self.assertTrue(user.is_active)

    def test_get_user(self):
        user = User.objects.create(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            email=faker.email(),
            password=make_password("StrongPassword"),
        )

        self.client.force_authenticate(user=user)

        response = self.client.get(reverse("users-list"))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data.get("count"), User.objects.count())
        self.assertContains(response, f"{user.first_name} {user.last_name}")
