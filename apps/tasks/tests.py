from datetime import timedelta

from django.conf import settings
from django.core import mail
from django.urls import reverse
from django.utils.timezone import utc

from faker import Faker

from rest_framework.exceptions import ValidationError
from rest_framework.status import HTTP_200_OK
from rest_framework.status import HTTP_201_CREATED
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.tasks.helpers import start_month_date
from apps.tasks.models import Task
from apps.tasks.models import Comment
from apps.tasks.models import TimeLog
from apps.tasks.models import Timer
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

        self.assertNotEqual(self.task.owner, other_owner)
        self.task.refresh_from_db()
        self.assertEqual(self.task.owner.pk, other_owner.pk)

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

    def test_top_month_tasks(self):
        task_2 = Task.objects.create(
            title=fake.word(),
            description=fake.text(),
            owner=self.user,
            status=Task.Status.IN_PROGRESS
        )
        timelog_1 = TimeLog.objects.create(
            started_at=fake.date_time().replace(tzinfo=utc) - timedelta(days=31),
            duration=timedelta(days=15),
            task_id=self.task.id,
            owner_id=self.user.id
        )
        timelog_2 = TimeLog.objects.create(
            started_at=start_month_date(),
            duration=timedelta(minutes=25),
            task_id=task_2.id,
            owner_id=self.user.id
        )

        response = self.client.get(reverse("tasks-top-month-duration"))

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIsNot(response.data[0].get("id"), timelog_1.id)
        self.assertEqual(response.data[0].get("id"), timelog_2.id)
        self.assertEqual(self.task, timelog_1.task)


class CommentTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(
            email=fake.email(),
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
        self.comment = Comment.objects.create(
            task=self.task,
            owner=self.user,
            text=fake.text()
        )

    def test_create_comment(self):
        data = {
            "task": self.task.id,
            "text": fake.text()
        }

        response = self.client.post(reverse("comments-list"), data)

        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]

        self.assertEqual(sent_email.subject, "Your task got a new comment!")
        self.assertIn(f"The task \"{self.task.title}\""
                      f" got a new comment :\n {data.get('text')}", sent_email.body)
        self.assertEqual(sent_email.from_email, settings.EMAIL_HOST_USER)
        self.assertEqual(sent_email.to, [self.user.email])

        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_list_comments(self):
        comment = Comment.objects.create(task_id=self.task.id, owner=self.user, text=fake.text())

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
        self.user = User.objects.create(
            email=fake.email(),
            password=fake.password()
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
        self.timer = Timer.objects.create(
            task=self.task,
            owner=self.user,
            is_started=False,
        )
        self.timelog = TimeLog.objects.create(
            started_at=fake.date_time().replace(tzinfo=utc),
            duration=timedelta(minutes=30),
            task=self.task,
            owner=self.user
        )

    def test_start_timer(self):
        response = self.client.post(reverse("tasks-start", kwargs={"pk": self.task.id}))

        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_stop_timer(self):
        self.timer.is_started = True
        self.timer.save()
        response = self.client.post(reverse("tasks-stop", kwargs={"pk": self.task.id}))

        self.assertEqual(response.status_code, HTTP_200_OK)

        self.timer.is_started = False
        with self.assertRaises(ValidationError):
            self.timer.stop()

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
            "started_at": fake.date_time().replace(tzinfo=utc),
            "duration": timedelta(minutes=90),
            "task": self.task.pk,
            "owner": self.user.pk
        }

        response = self.client.patch(reverse("timelog-detail", kwargs={"pk": self.timelog.id}), data)

        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_remove_timelog(self):
        response = self.client.delete(reverse("timelog-detail", kwargs={"pk": self.timelog.id}))
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
