from datetime import timedelta

from django.db.models import Manager
from django.db.models import Sum
from django.utils import timezone

from apps.tasks.helpers import start_month_date


class LastMonthTaskManager(Manager):

    def total_duration(self):
        queryset = self.filter(time_logs__started_at__gte=start_month_date())

        return queryset.annotate(
            total_duration=Sum("time_logs__duration")
        ).filter(total_duration__isnull=False)


class TaskWithTotalTimeManager(Manager):

    def last_month(self, owner):
        return self.filter(
            owner=owner,
            started_at__gte=start_month_date(),
            started_at__lte=timezone.now()
        ).aggregate(total=Sum("duration"))
