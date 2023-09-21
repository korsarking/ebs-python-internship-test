from django.conf import settings
from django.core import mail
from django.urls import reverse
from faker import Faker
from rest_framework.status import HTTP_200_OK
from rest_framework.status import HTTP_201_CREATED
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.tasks.models import Comment
from apps.tasks.models import Task
from apps.users.models import User

fake = Faker()


class TaskTestCase(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(email=fake.email(), password=fake.password())
        self.client.force_authenticate(user=self.user)

        self.task = Task.objects.create(
            title=fake.word(),
            description=fake.text(),
            owner=self.user,
            status=Task.Status.IN_PROGRESS
        )

    def test_create_task(self):
        data = {
            "title": fake.word(),
            "description": fake.text(),
            "status": Task.Status.IN_PROGRESS,
        }

        response = self.client.post(reverse("tasks-list"), data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_get_task_list(self):
        response = self.client.get(reverse("tasks-list"))
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_get_task_by_id(self):
        response = self.client.get(reverse("tasks-detail", kwargs={"pk": self.task.id}))
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_filter_by_status(self):
        response = self.client.get(reverse("tasks-list"), data={"status": "completed"})
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_assign_task(self):
        other_owner = User.objects.create(email=fake.email())
        data = {"owner": other_owner.pk}

        response = self.client.patch(reverse("tasks-detail", kwargs={"pk": self.task.id}), data)
        self.assertEqual(response.status_code, HTTP_200_OK)

        self.task.refresh_from_db()

        self.assertEqual(self.task.owner.pk, other_owner.pk)

        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]

        self.assertEqual(sent_email.subject, "You have been assigned to a new task!")
        self.assertIn("You have been assigned to a new task!", sent_email.body)
        self.assertEqual(sent_email.from_email, settings.EMAIL_HOST_USER)
        self.assertEqual(sent_email.to, [other_owner.email])

    def test_complete_task(self):
        Comment.objects.create(
            text=fake.word(),
            task=self.task,
            owner=self.user,
        )

        self.task.status = Task.Status.IN_PROGRESS
        self.task.save()

        response = self.client.patch(
            reverse(
                "tasks-detail",
                kwargs={"pk": self.task.pk}
            ),
            data={"status": Task.Status.COMPLETED}
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.COMPLETED)

    def test_remove_task(self):
        response = self.client.delete(reverse("tasks-detail", kwargs={"pk": self.task.id}))
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

    def test_search_task(self):
        response = self.client.get(reverse("tasks-list"), data={"search": "found"})
        self.assertEqual(response.status_code, HTTP_200_OK)


class CommentTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(
            email=fake.email,
            password=fake.password
        )
        self.client.force_authenticate(
            user=self.user,
            token=f"Bearer {RefreshToken.for_user(self.user)}"
        )
        self.task = Task.objects.create(
            title=fake.word(),
            description=fake.text(),
            owner=self.user
        )

    def test_create_comment(self):
        data = {
            "task": self.task.id,
            "text": fake.text()
        }

        response = self.client.post(reverse("comments-list"), data)

        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_list_comments(self):
        comment = Comment.objects.create(task_id=self.task.id, owner=self.user, text=fake.text())

        response = self.client.get(reverse("comments-list"), data={"task": self.task.id})

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(self.task.title, comment.task.title)
