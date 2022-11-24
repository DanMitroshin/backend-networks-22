

def get_activity_metric_name(metric_object, metric_category, metric_value, metric_border):
    return f'{metric_object}__{metric_category}__{metric_value}__{str(metric_border)}'


def timedelta_to_dhms(duration):
    # преобразование в дни, часы, минуты и секунды
    days, seconds = duration.days, duration.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    return days, hours, minutes, seconds
