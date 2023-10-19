import random
from datetime import timedelta

import factory
from factory import fuzzy
from factory.django import DjangoModelFactory

from apps.tasks.models import Task
from apps.tasks.models import TimeLog
from apps.tasks.models import Timer
from apps.tasks.models import Comment
from apps.users.factories import UserFactory


class TaskFactory(DjangoModelFactory):
    class Meta:
        model = Task

    title = factory.Faker("text")
    description = factory.Faker("text")
    owner = factory.SubFactory(UserFactory)
    status = fuzzy.FuzzyChoice(Task.Status.values)


class CommentFactory(DjangoModelFactory):
    class Meta:
        model = Comment

    text = factory.Faker("text")
    owner = factory.SubFactory(UserFactory)
    task = factory.SubFactory(TaskFactory)


class TimeLogFactory(DjangoModelFactory):
    class Meta:
        model = TimeLog

    task = factory.SubFactory(TaskFactory)
    owner = factory.SubFactory(UserFactory)

    @factory.lazy_attribute
    def duration(self):
        random_duration = timedelta(minutes=random.randint(1, 120))
        return random_duration


class TimerFactory(DjangoModelFactory):
    class Meta:
        model = Timer

    task = factory.SubFactory(TaskFactory)
    owner = factory.SubFactory(UserFactory)
