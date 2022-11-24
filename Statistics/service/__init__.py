from datetime import timedelta
from django.utils import timezone

from Statistics.constants import METRICS
from Statistics.models import MetricsCache
from .activity import create_activity_log


def add_value_to_metric(value, metric_name, delta_day=0):
    # RIGHT_ANSWERS_AMOUNT = "right_answers_amount"
    if delta_day == 0:
        day = timezone.datetime.utcnow().date()
    else:
        day = timezone.datetime.utcnow().date() - timedelta(days=delta_day)
    metric = MetricsCache.objects.filter(day=day, metric=metric_name)
    if metric.exists():
        item = metric.first()
        item.value = int(item.value) + value
        item.average += value / 30.0
        item.save()
    else:
        item = MetricsCache.objects.create(
            day=day,
            metric=metric_name,
            value=value,
            average=value / 30.0,
        )

        prev_day = MetricsCache.objects.filter(day=day - timezone.timedelta(days=1), metric=metric_name)
        if prev_day.exists():
            average = prev_day.first().average * 30.0
            data_day30 = day - timezone.timedelta(days=30)
            metric_30 = MetricsCache.objects.filter(day=data_day30, metric=metric_name)

            if metric_30.exists():
                average = average - int(metric_30.first().value)
            item.average += average / 30.0

        item.save()


def add_right_answers_amount_to_metric(value):
    add_value_to_metric(value, METRICS.RIGHT_ANSWERS_AMOUNT)


def add_total_answers_amount_to_metric(value):
    add_value_to_metric(value, METRICS.TOTAL_ANSWERS_AMOUNT)


def add_ratings_requests_amount(value=1):
    add_value_to_metric(value, METRICS.RATING_REQUEST_AMOUNT)


def add_subscription_prices_requests_amount(value=1):
    add_value_to_metric(value, METRICS.SUBSCRIPTION_PRICES_REQUEST_AMOUNT)


def add_answers_to_app_metrics(right_answers=0, total_answers=0):
    try:
        add_right_answers_amount_to_metric(right_answers)
        add_total_answers_amount_to_metric(total_answers)
    except:
        pass
