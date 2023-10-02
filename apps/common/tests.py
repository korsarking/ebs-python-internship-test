from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

class TestCommon(APITestCase):

    def test_health_view(self):
        response = self.client.get(reverse("health_view"))
        self.assertEqual(response.status_code, 200)
