import json

from Statistics.models import ActivityLog


def create_activity_log(user, activity, payload=None):
    log_dict = {
        "user": user,
        "activity": activity
    }

    if payload is not None:
        if type(payload) == str:
            log_dict["payload"] = payload
        else:
            log_dict["payload"] = json.dumps(payload)

    try:
        ActivityLog.objects.create(**log_dict)
    except:

        try:
            max_length = ActivityLog._meta.get_field('activity').max_length
            log_dict["activity"] = activity[:max_length - 1] + "$"

            ActivityLog.objects.create(**log_dict)
        except:
            pass
