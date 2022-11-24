import datetime
from collections import defaultdict

from Statistics.models import ProductLog, ProductProgress, TrainerBlockProgress
from Users.models import User


def slice_by_date(queryset, begin, end=None, date_field_name='timestamp'):
    current_day = begin
    if end is None:
        end = begin + datetime.timedelta(days=1)

    result = []
    while current_day < end:
        next_day = current_day + datetime.timedelta(days=1)
        result.append(queryset.filter(**{
            f'{date_field_name}__gte': current_day,
            f'{date_field_name}__lt': next_day
        }))
        current_day = next_day
    return result


def get_activity_dict():
    user_ids = User.objects.all().values_list('id').distinct()
    result = defaultdict(list)
    print(ProductLog.objects.all().order_by('timestamp'))
    for day in slice_by_date(
        ProductLog.objects.all().prefetch_related('user'),
        begin=ProductLog.objects.all().order_by('timestamp').first().timestamp.date(),
        end=datetime.date.today() + datetime.timedelta(days=1)):

        for user_id in user_ids:
            result[user_id[0]].append(1 if day.filter(user__id=user_id[0]).exists() else 0)
    return result


def retention():
    activity_table = list(get_activity_dict().values())
    max_len = 0
    for row in activity_table:
        while len(row) > 0 and row[0] == 0:
            row.pop(0)
        if len(row) > max_len:
            max_len = len(row)

    retention_total = [0] * max_len
    for row in activity_table:
        for i in range(len(row)):
            retention_total[i] += row[i]

    result = []
    first_day_users = retention_total[0]
    for day in retention_total:
        result.append(day / first_day_users)

    result = list(zip(list(range(len(result))), result))
    return [{"name": str(days) + ' days', "value": retention_} for days, retention_ in result]
