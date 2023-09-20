from django.contrib.auth.hashers import make_password
from faker import Faker
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK
from rest_framework.test import APITestCase

from apps.users.models import User

faker = Faker()


class UserTestCase(APITestCase):
    def test_register_user(self):
        data = {
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "email": faker.email(),
            "password": faker.password(),
        }

        response = self.client.post(reverse("users-register"), data=data)
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
