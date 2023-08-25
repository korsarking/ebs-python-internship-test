from django.db import models

from apps.users.models import User
from apps.common.models import BaseModel


class Task(BaseModel):

    class Status(models.TextChoices):
        IN_WORK = "In work"
        COMPLETED = "Completed"

    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.IN_WORK)
