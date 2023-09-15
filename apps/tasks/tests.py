from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from faker import Faker
from rest_framework_simplejwt.tokens import RefreshToken

from apps.tasks.models import Task, Comment
from apps.users.models import User

fake = Faker()


class TaskTestCase(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create(email=fake.email(),
                                        password=fake.password())
        self.client.force_authenticate(user=self.user)
        self.task = Task.objects.create(title=fake.word(), description=fake.text(),
                                        assigned_to=self.user, user=self.user)

    def test_create_task(self):
        data = {
            "title": fake.word(),
            "description": fake.text(),
            "status": Task.Status.IN_WORK
        }

        response = self.client.post(reverse('tasks-list'), data)

        self.assertEqual(201, response.status_code)

    def test_list_tasks(self):
        Task.objects.create(title=fake.word(), assigned_to=self.user, user=self.user)

        response = self.client.get(reverse('tasks-list'))

        self.assertEqual(200, response.status_code)

    def test_list_tasks_by_id(self):
        task = Task.objects.create(title=fake.word(), assigned_to=self.user, user=self.user)

        response = self.client.get(reverse('tasks-detail', kwargs={'pk': task.id}))

        self.assertEqual(200, response.status_code)

    def test_completed_task(self):
        Task.objects.create(title=fake.word(), status=Task.Status.COMPLETED,
                            assigned_to=self.user, user=self.user)
        Task.objects.create(title=fake.word(), status=Task.Status.IN_WORK,
                            assigned_to=self.user, user=self.user)

        base_url = reverse('tasks-list')
        response = self.client.get(base_url + '?status=Completed')

        self.assertEqual(200, response.status_code)

    def test_assign_task(self):
        task = Task.objects.create(title=fake.word(), assigned_to=self.user,
                                   user=self.user)
        other_user = User.objects.create(email=fake.email())

        data = {
            "assigned_to": other_user.id,
            "title": fake.word(),
            "status": Task.Status
        }

        response = self.client.put(reverse('tasks-detail', kwargs={'pk': task.id}), data)

        self.assertEqual(200, response.status_code)

    def test_remove_task(self):
        task = Task.objects.create(title=fake.word(), assigned_to=self.user, user=self.user)

        response = self.client.delete(reverse('tasks-detail', kwargs={'pk': task.id}))

        self.assertEqual(204, response.status_code)

    def test_search_task(self):
        Task.objects.create(title=fake.word(), assigned_to=self.user, user=self.user)

        base_url = reverse('tasks-list')
        response = self.client.get(base_url + '?search=found')

        self.assertEqual(200, response.status_code)


class CommentTestCase(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create(email=fake.email, password=fake.password)
        self.client.force_authenticate(user=self.user, token=f'Bearer {RefreshToken.for_user(self.user)}')
        self.task = Task.objects.create(title=fake.word(), assigned_to=self.user, user=self.user)

    def test_create_comment(self):
        data = {
            "task": self.task.id,
            "text": fake.text()
        }

        response = self.client.post(reverse('comments-list'), data)

        self.assertEqual(201, response.status_code)

    def test_list_comments(self):
        comment = Comment.objects.create(task_id=self.task.id, user=self.user, text=fake.text())

        base_url = reverse('comments-list')

        response = self.client.get(base_url + f'?task={self.task.id}')

        self.assertEqual(200, response.status_code)

        self.assertEqual(self.task.title, comment.task.title)
