from Statistics.constants import USER_METRIC
from Statistics.models import UserMetric
from .get_metrics import get_user_metric
from Users.models import User


def update_user_metric(user_metric: UserMetric, new_value) -> UserMetric:
    user_metric.value = str(new_value)
    user_metric.save()
    return user_metric


def update_user_metric_with_function(
        user_metric: UserMetric, value=0, update_function=lambda old, new: int(old) + new) -> UserMetric:
    new_value = update_function(user_metric.value, value)
    return update_user_metric(user_metric, new_value)


def update_user_read_theory_blocks_amount(user: User, add_blocks_amount: int = 0) -> UserMetric:
    user_metric = get_user_metric(user, USER_METRIC.READ_THEORY_BLOCKS_AMOUNT)
    return update_user_metric_with_function(user_metric, add_blocks_amount)
