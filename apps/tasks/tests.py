from django.core import mail
from django.conf import settings
from django.urls import reverse

from faker import Faker

from rest_framework.status import HTTP_200_OK
from rest_framework.status import HTTP_201_CREATED
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.common.helpers import send_user_email
from apps.tasks.models import Comment
from apps.tasks.models import Task
from apps.users.models import User

from unittest.mock import patch

fake = Faker()


class TaskTestCase(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(email=fake.email(), password=fake.password())
        self.client.force_authenticate(user=self.user)

        self.task = Task.objects.create(
            title=fake.word(),
            description=fake.text(),
            assigned_to=self.user,
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
        self.assertEqual(HTTP_201_CREATED, response.status_code)

    def test_list_tasks(self):
        response = self.client.get(reverse("tasks-list"))
        self.assertEqual(HTTP_200_OK, response.status_code)

    def test_list_tasks_by_id(self):
        response = self.client.get(reverse("tasks-detail", kwargs={"pk": self.task.id}))
        self.assertEqual(HTTP_200_OK, response.status_code)

    def test_completed_task(self):
        response = self.client.get(reverse("tasks-list") + "?status=completed")
        self.assertEqual(HTTP_200_OK, response.status_code)

    @patch("apps.common.helpers.send_mail")
    def test_send_mail_emulation(self, mock_send_mail):
        mock_send_mail.return_value = True

        send_user_email(
            "test subject",
            "test message text",
            "user@gmail.com",
            ["user1@gmail.com"]
        )

        mock_send_mail.assert_called_once_with(
            subject="test subject",
            message="test message text",
            from_email="user@gmail.com",
            recipient_list=["user1@gmail.com"]
        )

    def test_assign_task(self):
        other_owner = User.objects.create(email=fake.email())
        data = {
            "status": Task.Status.ASSIGNED,
            "title": fake.word()
        }

        url = reverse("tasks-assign", kwargs={"pk": self.task.id, "assigned_to": other_owner.pk})
        response = self.client.patch(url, data)
        self.assertEqual(HTTP_204_NO_CONTENT, response.status_code)

        self.task.refresh_from_db()

        self.assertEqual(self.task.assigned_to.pk, other_owner.pk)

        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]

        self.assertEqual(sent_email.subject, "You have been assigned to a new task!")
        self.assertIn("You have been assigned to a new task!", sent_email.body)
        self.assertEqual(sent_email.from_email, settings.EMAIL_HOST_USER)
        self.assertEqual(sent_email.to, [other_owner.email])

    def test_remove_task(self):
        response = self.client.delete(reverse("tasks-detail", kwargs={"pk": self.task.id}))
        self.assertEqual(HTTP_204_NO_CONTENT, response.status_code)

    def test_search_task(self):
        response = self.client.get(reverse("tasks-list") + "?search=found")
        self.assertEqual(HTTP_200_OK, response.status_code)


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
            assigned_to=self.user,
            owner=self.user
        )

    def test_create_comment(self):
        data = {
            "task": self.task.id,
            "text": fake.text()
        }

        response = self.client.post(reverse("comments-list"), data)

        self.assertEqual(HTTP_201_CREATED, response.status_code)

    def test_list_comments(self):
        comment = Comment.objects.create(task_id=self.task.id, owner=self.user, text=fake.text())

        response = self.client.get(reverse("comments-list") + f"?task={self.task.id}")

        self.assertEqual(HTTP_200_OK, response.status_code)
        self.assertEqual(self.task.title, comment.task.title)

    def test_send_email_on_comment(self):
        comment = Comment.objects.create(
            owner=self.task.owner,
            task=self.task,
            text=fake.text()
        )

        url = reverse("tasks-detail", kwargs={"pk": self.task.id})
        validated_data = {"status": Task.Status.COMPLETED}
        response = self.client.patch(url, validated_data)

        self.assertEqual(HTTP_200_OK, response.status_code)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.COMPLETED)

        with patch("apps.common.helpers.send_mail") as mock_send_user_email:
            send_user_email(
                subject="Your task, that was commented is completed!",
                message=f"You have just executed a task!\n The completed task is {self.task.title}.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[comment.owner.email]
            )

            mock_send_user_email.assert_called_once_with(
                subject="Your task, that was commented is completed!",
                message=f"You have just executed a task!\n The completed task is {self.task.title}.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[comment.owner.email]
            )
