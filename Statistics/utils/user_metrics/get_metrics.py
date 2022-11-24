from Statistics.constants import USER_METRIC
from Statistics.models import UserMetric
from Users.models import User


def get_user_metric(user, metric, default_value=None):
    user_metric, created = UserMetric.objects.get_or_create(metric=metric, user=user)
    if default_value is not None:
        user_metric.value = default_value
    return user_metric


def get_user_success_answers_amount(user: User):
    user_metric = get_user_metric(user, USER_METRIC.SUCCESS_ANSWERS_AMOUNT)
    return int(user_metric.value)


def get_user_read_theory_blocks_amount(user: User):
    user_metric = get_user_metric(user, USER_METRIC.READ_THEORY_BLOCKS_AMOUNT)
    return int(user_metric.value)
