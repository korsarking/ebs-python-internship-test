from django.db import models

from apps.users.models import User
from apps.common.models import BaseModel


class Task(BaseModel):
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress"
        COMPLETED = "completed"

    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.IN_PROGRESS)


class Comment(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()

    class Meta:
        ordering = ["-id"]
