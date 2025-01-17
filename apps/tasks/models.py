from django.utils import timezone
from django.db import models

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
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.IN_PROGRESS)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")

    objects = LastMonthTaskManager()

    class Meta:
        db_table = "tasks"


class Comment(BaseModel):
    text = models.TextField()
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")

    class Meta:
        db_table = "comments"


class TimeLog(BaseModel):
    started_at = models.DateTimeField(default=timezone.now)
    duration = models.DurationField(null=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="time_logs")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="time_logs")

    objects = TaskWithTotalTimeManager()

    class Meta:
        db_table = "time_logs"


class Timer(BaseModel):
    started_at = models.DateTimeField(default=timezone.now)
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
        duration = timezone.now() - self.started_at

        self.is_started = False
        self.duration = duration
        self.started_at = timezone.localtime(self.started_at)
        self.save(update_fields=["is_started", "started_at"])

        TimeLog.objects.create(owner=self.owner, task=self.task, duration=duration, started_at=self.started_at)
