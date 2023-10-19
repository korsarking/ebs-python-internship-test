from apps.users.models import User
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


class TestCommon(APITestCase):

    fixtures = ["users"]

    def setUp(self) -> None:
        self.test_user1 = User.objects.get(email="user1@email.com")
        self.client.force_authenticate(user=self.test_user1)

    def test_health_view(self):
        response = self.client.get(reverse("health_view"))
        self.assertEqual(response.status_code, 200)
