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
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="created_task")
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reassign_owner', null=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.IN_WORK)


class Comment(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="task_of_comment")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="users_comment")
    text = models.CharField(max_length=255)

    class Meta:
        ordering = ['-id']
