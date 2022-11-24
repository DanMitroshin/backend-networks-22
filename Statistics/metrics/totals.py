import datetime

from Users.models import BannedUser
from Users.utils.permissions import check_has_content_access
from .utils import aggregate
from django.utils import timezone
from django.db import models
from Statistics.utils import update_achievement_rating, update_best_week_place_user, \
    get_week_best_place_user

from Statistics.models import ProductLog, InitLog, WeekRating
from Users.constants import DEVICES, CAN_NOT_PARTICIPATE_IN_RATING_AND_EDIT_INFORMATION


def total_product_completes_per_day():
    queryset = ProductLog.objects.filter().prefetch_related('product')
    values = [
        {
            'date': item.timestamp.date(),
            'completed': 1,
        } for item in queryset
    ]
    return aggregate(
        values,
        lambda x: sum(x),
        'completed',
        group_by='date',
    )


def total_user_completes_per_day():
    queryset = ProductLog.objects.filter().prefetch_related('user')
    values = []
    dates = dict()

    for item in queryset:
        date = item.timestamp.date()
        if date not in dates:
            dates[date] = set()
        if item.user.id not in dates[date]:
            dates[date].add(item.user.id)
            values.append({
                'user': item.user,
                'date': item.timestamp.date(),
                'completed': 1,
            })
    return aggregate(
        values,
        lambda x: sum(x),
        'completed',
        group_by='date',
    )


def total_product_completes_per_user():
    queryset = ProductLog.objects.all().prefetch_related('user', 'product')
    values = [
        {
            'user': item.user.id,
            'completed': 1,
        } for item in queryset
    ]
    result = aggregate(
        values,
        lambda x: sum(x),
        'completed',
        group_by='user',
    )
    result.sort(key=lambda x: -x['value'])
    return result


def total_unique_users_from_init_per_day():
    queryset = InitLog.objects.filter().prefetch_related('user')
    values = []
    dates = dict()

    for item in queryset:
        date = item.timestamp.date()
        if date not in dates:
            dates[date] = set()
        if item.user.id not in dates[date]:
            dates[date].add(item.user.id)
            values.append({
                'user': item.user,
                'date': item.timestamp.date(),
                'completed': 1,
            })
    return aggregate(
        values,
        lambda x: sum(x),
        'completed',
        group_by='date',
    )


def total_inits_per_day():
    queryset = InitLog.objects.filter().prefetch_related('user')
    values = []
    dates = dict()

    for item in queryset:
        values.append({
            'user': item.user,
            'date': item.timestamp.date(),
            'completed': 1,
        })
    return aggregate(
        values,
        lambda x: sum(x),
        'completed',
        group_by='date',
    )


####################################
# WEEK RATING #

def get_user_rating_name(user):
    # name = ""
    if user.first_name or user.last_name:
        return f'{user.first_name} {user.last_name}'
    return user.get_nickname()


def create_rating():
    queryset = ProductLog.objects.all()[0:20]
    for item in queryset:
        try:
            item_data = WeekRating.objects.filter(user=item.user, status=0)
            if item_data.exists():
                item_data.update(value=models.F('value') + item.completed)
            else:
                WeekRating.objects.create(user=item.user, value=item.completed, status=0)
        except:
            continue

    q = WeekRating.objects.filter(status=0)
    return [{'u': get_user_rating_name(item.user), 'r': item.value} for item in q]


def get_user_rating_info(user):
    queryset = WeekRating.objects.filter(status=0)
    counter = 1
    for item in queryset:
        # print("ID", item.id, user.id)
        if item.user.id == user.id:
            return {"place": counter, "u": get_user_rating_name(item.user), "r": item.value}
        counter += 1
    return {"error": "Чтобы попасть в рейтинг, необходимо дать правильные ответы в тестах!"}


def delete_rating():
    WeekRating.objects.filter(status=0).delete()
    return []


def create_production_week_rating(date_str="2021-04-05"):
    delete_rating()
    date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    date = date.replace(hour=0, minute=1)
    queryset = ProductLog.objects.filter(timestamp__gte=date, product__lesson_type__in=['p2', 'p3'])

    for item in queryset:
        item_data = WeekRating.objects.filter(user=item.user, status=0)
        if item_data.exists():
            item_data.update(value=models.F('value') + item.completed)
        else:
            WeekRating.objects.create(user=item.user, value=item.completed, status=0)
    return "ok"


def get_rating(top_n=70):
    def get_best_place(rating_item):
        try:
            place = rating_item.best_place
            if type(place) == int:
                return place
            return -1
        except:
            return -1

    q = WeekRating.objects.filter(status=0)[:top_n] if top_n > 0 else WeekRating.objects.filter(status=0)
    if len(q) < 7 and (top_n == -1 or top_n >= 7):
        return []
    return [{'u': get_user_rating_name(item.user), 'r': item.value, 'bp': get_best_place(item)} for item in q]


def update_rating(user, completed, has_ban=None):
    if completed == 0:
        return

    if has_ban is None:
        ban_info = BannedUser.objects.filter(
            user=user,
            type=CAN_NOT_PARTICIPATE_IN_RATING_AND_EDIT_INFORMATION)
        if ban_info.exists():
            has_ban = True

    if has_ban:
        return

    queryset = WeekRating.objects.filter(user=user, status=0)
    if queryset.exists():
        queryset.update(value=models.F('value') + completed)
    else:
        best_place = get_week_best_place_user(user)
        WeekRating.objects.create(user=user, value=completed, status=0, best_place=best_place)


def create_new_week_rating():
    queryset = WeekRating.objects.filter(status=0)
    place = 1
    users_with_codes = []
    for item in queryset:
        # update best week place metric:
        update_best_week_place_user(item.user, place)

        # update achievements:
        ach = update_achievement_rating(item.user, place)
        if place <= 50:
            item.user.coins += 100 * (51 - place)
            item.user.save()
        place += 1
        try:
            if 'top_n' in ach.keys():
                if (not check_has_content_access(item.user)) and (item.user.device != DEVICES.APPLE):
                    users_with_codes.append({'user': item.user, 'result': ach['top_n']})
        except:
            continue
    WeekRating.objects.filter(status=1).delete()
    users = [item.user.id for item in WeekRating.objects.filter(status=0)[:3]]
    WeekRating.objects.filter(status=0, user__id__in=users).update(status=1)
    WeekRating.objects.filter(status=0).delete()
    return []  # [{'u': get_user_rating_name(item.user), 'r': item.value} for item in WeekRating.objects.all()]


def get_previous_week_leaders():
    return [{'u': get_user_rating_name(item.user), 'r': item.value} for item in
            WeekRating.objects.filter(status=1)]


def get_expired_week_time():
    now_time = timezone.datetime.now()
    current_day = now_time.date().weekday()
    current_time = now_time.hour
    current_min = now_time.minute
    return {"d": 6 - current_day, "h": 23 - current_time, "m": 60 - current_min}
