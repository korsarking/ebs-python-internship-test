from datetime import timedelta
from unittest import mock

from django.conf import settings
from django.core import mail
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone
from faker import Faker
from rest_framework.status import HTTP_200_OK
from rest_framework.status import HTTP_201_CREATED
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.tasks.factories import CommentFactory
from apps.tasks.factories import TaskFactory
from apps.tasks.factories import TimeLogFactory
from apps.tasks.factories import TimerFactory
from apps.tasks.helpers import start_month_date
from apps.tasks.models import Task
from apps.users.factories import UserFactory

fake = Faker()


class TaskTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = UserFactory.create()
        self.client.force_authenticate(user=self.user)

        self.task = TaskFactory.create()

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

    @mock.patch("apps.tasks.serializers.send_mail")
    def test_assign_task(self, mock_send_email):
        mock_send_email.return_value = None
        other_owner = UserFactory.create()
        data = {"owner": other_owner.pk}

        response = self.client.patch(reverse("tasks-detail", kwargs={"pk": self.task.id}), data)
        self.assertEqual(response.status_code, HTTP_200_OK)

        self.assertNotEqual(self.task.owner, other_owner)
        self.task.refresh_from_db()
        self.assertEqual(Task.objects.get(id=self.task.id).owner, other_owner)

    @mock.patch("apps.tasks.serializers.send_mail")
    def test_complete_task(self, mock_send_email):
        mock_send_email.return_value = None
        CommentFactory.create(task=self.task, owner=self.user)
        self.task.status = Task.Status.IN_PROGRESS
        self.task.save()

        response = self.client.patch(
            reverse("tasks-detail", kwargs={"pk": self.task.pk}), data={"status": Task.Status.COMPLETED}
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(Task.objects.get(id=self.task.id).status, Task.Status.COMPLETED)

    def test_remove_task(self):
        response = self.client.delete(reverse("tasks-detail", kwargs={"pk": self.task.id}))
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

    def test_search_task(self):
        response = self.client.get(reverse("tasks-list"), data={"search": "found"})
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_top_month_tasks(self):
        timelog1 = TimeLogFactory.create(started_at=timezone.now() - timedelta(days=31))
        timelog2 = TimeLogFactory.create()
        date_month = timezone.now().strftime("%m")
        response = self.client.get(reverse("tasks-top-month-duration"))

        count_of_tasks_in_response = Task.objects.filter(time_logs__started_at__gte=start_month_date()).count()

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertNotEqual(date_month, timelog1.started_at.strftime("%m"))
        self.assertEqual(date_month, timelog2.started_at.strftime("%m"))
        self.assertEqual(len(response.json()), count_of_tasks_in_response)
        self.assertEqual(response.data[0].get("id"), timelog2.task_id)

    def test_send_mail(self):
        mail_data = {
            "subject": "This is test subject",
            "message": "This is test message or text",
            "from_email": settings.EMAIL_HOST_USER,
            "recipient_list": [settings.DEFAULT_FROM_EMAIL],
        }

        send_mail(
            subject=mail_data["subject"],
            message=mail_data["message"],
            from_email=mail_data["from_email"],
            recipient_list=mail_data["recipient_list"],
        )
        sent_email = mail.outbox[0]

        self.assertEqual(sent_email.subject, "This is test subject")
        self.assertIn("This is test message or text", sent_email.body)
        self.assertEqual(sent_email.from_email, settings.EMAIL_HOST_USER)
        self.assertEqual(sent_email.to, [settings.DEFAULT_FROM_EMAIL])


class CommentTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = UserFactory.create(password=fake.password)
        self.client.force_authenticate(user=self.user, token=f"Bearer {RefreshToken.for_user(self.user)}")
        self.task = TaskFactory.create(owner=self.user)
        self.comment = CommentFactory.create(task=self.task, owner=self.user)

    @mock.patch("apps.tasks.serializers.send_mail")
    def test_create_comment(self, mock_send_email):
        mock_send_email.return_value = None
        data = {"task": self.task.id, "text": fake.text()}
        response = self.client.post(reverse("comments-list"), data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_list_comments(self):
        comment = CommentFactory.create(task_id=self.task.id, owner=self.user)

        response = self.client.get(reverse("comments-list"), data={"task": self.task.id})

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(self.task.title, comment.task.title)

    def test_remove_comment(self):
        response = self.client.delete(reverse("comments-detail", kwargs={"pk": self.comment.id}))
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

    def test_search_comment(self):
        response = self.client.get(reverse("comments-list"), data={"search": "found"})
        self.assertEqual(response.status_code, HTTP_200_OK)


class TimerTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = UserFactory.create(password=fake.password)
        self.client.force_authenticate(user=self.user, token=f"Bearer {RefreshToken.for_user(self.user)}")
        self.task = TaskFactory.create(owner=self.user)
        self.timer = TimerFactory.create(
            task=self.task,
            owner=self.user,
        )
        self.timelog = TimeLogFactory.create()

    def test_start_timer(self):
        response = self.client.post(reverse("tasks-start", kwargs={"pk": self.task.id}))

        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_stop_timer(self):
        self.timer.is_started = True
        self.timer.save(update_fields=["is_started"])

        response = self.client.post(reverse("tasks-stop", kwargs={"pk": self.task.id}))
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_stop_timer_with_no_ongoing_timer(self):
        self.timer.is_started = False
        self.timer.save()

        response = self.client.post(reverse("tasks-stop", kwargs={"pk": self.task.id}))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"detail": f"Task id:{self.timer.id} has no ongoing timer."})

    def test_create_timelog(self):
        data = {
            "date_field": fake.date(),
            "duration_minutes": fake.random_number(2),
            "task": self.task.id,
        }
        response = self.client.post(reverse("timelog-list"), data)

        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_get_timelog_list(self):
        response = self.client.get(reverse("timelog-list"))

        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_full_time_by_month(self):
        response = self.client.get(reverse("timelog-last-month-full-time"))

        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_update_timelog(self):
        data = {
            "started_at": timezone.now() - timedelta(days=15),
            "duration": timedelta(minutes=90),
            "task": self.task.pk,
            "owner": self.user.pk,
        }

        response = self.client.patch(reverse("timelog-detail", kwargs={"pk": self.timelog.id}), data)

        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_remove_timelog(self):
        response = self.client.delete(reverse("timelog-detail", kwargs={"pk": self.timelog.id}))
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
