import string
import random

from django.utils import timezone

from Users.models import UserInfoVersion, BannedUser, User
from Users.constants import DEVICES, CAN_NOT_PARTICIPATE_IN_RATING_AND_EDIT_INFORMATION


def delete_inactive_bans():
    date = timezone.now().date()
    queryset = BannedUser.objects.filter(end_day__lt=date)
    amount = len(queryset)
    queryset.delete()

    return {'delete': amount}


def get_random_code(n, amount=5):
    letters = string.ascii_lowercase + string.ascii_uppercase + '0123456789'
    rand_string = ''.join(random.choice(letters) for _ in range(amount))
    return f'GIFT{rand_string}{7 * (n + 1)}_RAT'


def get_sale_info_for_user(user: User, amount_inits, has_access_content):
    try:
        info = UserInfoVersion.objects.get(user=user)
        if amount_inits < 2 or has_access_content:
            return None
        else:
            if user.device == DEVICES.ANDROID and info.notification_version < 8:  # 8 is current
                return None
            # ...
    except:
        pass
    return None


def get_ban_info_about_user(user):
    has_ban = False
    limit = ""
    ban_info = BannedUser.objects.filter(user=user,
                                         type=CAN_NOT_PARTICIPATE_IN_RATING_AND_EDIT_INFORMATION)
    if ban_info.exists():
        has_ban = True
        ban = ban_info.first()
        limit = f"Действует ограничение на участие в рейтинге до {ban.end_day}."

    return has_ban, {'limit': limit}
