from django.utils import timezone
from django.db import models

from rest_framework.exceptions import ValidationError

from apps.tasks.managers import TaskWithTotalTimeManager
from apps.tasks.managers import LastMonthTaskManager
from apps.common.models import BaseModel
from apps.users.models import User


class Task(BaseModel):
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress"
        COMPLETED = "completed"

    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.IN_PROGRESS)

    objects = LastMonthTaskManager()

    class Meta:
        db_table = "tasks"



class Comment(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()

    class Meta:
        db_table = "task_comments"


class TimeLog(models.Model):
    started_at = models.DateTimeField(default=timezone.now)
    duration = models.DurationField(null=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="time_logs")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="time_logs")

    objects = TaskWithTotalTimeManager()

    class Meta:
        db_table = "time_records"


class Timer(models.Model):
    started_at = models.DateTimeField(auto_now_add=True)
    is_started = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="timers")
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="timers")

    class Meta:
        db_table = "timer"

    def start(self):
        if not self.is_started:
            self.is_started = True
            self.started_at = timezone.now()
            self.save(update_fields=["is_started", "started_at"])

    def stop(self):
        if self.is_started:
            duration = timezone.now() - self.started_at

            self.is_started = False
            self.duration = duration
            self.started_at = timezone.localtime(self.started_at)
            self.save(update_fields=["is_started", "started_at"])

            TimeLog.objects.create(
                owner=self.owner,
                task=self.task,
                duration=duration,
                started_at=self.started_at
            )
        else:
            raise ValidationError({"detail": f"Task id:{self.id} has no ongoing timer."})
