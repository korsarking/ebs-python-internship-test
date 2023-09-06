from django.db import models

from apps.users.models import User
from apps.common.models import BaseModel


class Task(BaseModel):
    class Status(models.TextChoices):
        IN_WORK = "In work"
        COMPLETED = "Completed"
        ASSIGNED = "Assigned"

    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="tasks")
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner', null=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.IN_WORK)


class Comment(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.CharField(max_length=255)
