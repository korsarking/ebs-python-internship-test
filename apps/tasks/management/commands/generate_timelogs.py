import random
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.timezone import utc
from faker import Faker
from randomtimestamp import randomtimestamp

from apps.tasks.models import Task
from apps.tasks.models import TimeLog
from apps.users.models import User

fake = Faker()


class Command(BaseCommand):
    help = "create random timelogs for any users in DB"

    def add_arguments(self, parser):
        parser.add_argument("instances", type=int, help="number of timelogs instances")

    @transaction.atomic
    def handle(self, *args, **kwargs):
        if not kwargs.get("instances") or kwargs.get("instances") < 0:
            return self.stderr.write('Missing "instances" as argument.')

        instances_number = kwargs.get("instances")

        User.objects.bulk_create(
            [
                User(email=fake.email(), first_name=fake.first_name(), last_name=fake.last_name())
                for _ in range(instances_number)
            ],
            ignore_conflicts=True,
        )
        users = User.objects.all()

        Task.objects.bulk_create(
            [
                Task(
                    title=fake.word(),
                    description=fake.text(),
                    owner=random.choice(users),
                    status=random.choice(Task.Status.values),
                )
                for _ in range(instances_number)
            ]
        )
        tasks = Task.objects.all()

        TimeLog.objects.bulk_create(
            [
                TimeLog(
                    started_at=fake.date_time().replace(tzinfo=utc),
                    duration=datetime.today() - randomtimestamp(),
                    task=random.choice(tasks),
                    owner=random.choice(users),
                )
                for _ in range(instances_number)
            ],
            ignore_conflicts=True,
        )

        self.stdout.write(self.style.SUCCESS(f"Successfully created {instances_number} timelogs."))
