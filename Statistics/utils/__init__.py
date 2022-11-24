from Statistics.constants import USER_METRIC
from Statistics.models import TrainerBlockProgress, ProductLog, Achievement, UserMetric, AnswersProgressState
from Users.models import UserAchievementRelation
from Content.models import Associate
from Statistics.models import InitLog
from Services.utils.push_notifications import (
    send_notification_by_user,
)
import json
from django.utils import timezone
import datetime

from Content.constants import LESSON_TYPES


def get_last_init_timestamp(user):
    try:
        if user.last_entry:
            return user.last_entry
        return timezone.datetime.utcnow()
    except:
        return timezone.datetime.utcnow()


def get_new_achievements(user, timestamp):
    return [{"name": item.achieve.name, "description": item.achieve.description}
            for item in UserAchievementRelation.objects.filter(
            user=user.id,
            timestamp__gt=timestamp + datetime.timedelta(minutes=1))]


def update_enters(user, date=None, has_access_content=False):
    if date is None:
        date = timezone.now().date()
    prog, created = UserMetric.objects.get_or_create(metric="enters", user=user)
    answer = dict()
    bet = 50
    subscription_multiplier = 10
    multiplier = subscription_multiplier if has_access_content else 1
    if created:
        answer["current"] = 1
        answer["best"] = 1
        answer["bet"] = bet
        coins = bet * multiplier
        answer["coins"] = coins
        answer["tomorrowCoins"] = bet * 2
        answer["tomorrowMultiplier"] = 2
        answer["subscriptionShow"] = False
        user.coins += coins
        user.save()
        prog.value = json.dumps({"current": 1, "best": 1, "date": str(date)})
        prog.save()
    else:
        value = json.loads(prog.value)
        v_date = datetime.datetime.strptime(value["date"], "%Y-%m-%d").date()
        if date - timezone.timedelta(days=1) == v_date:
            value["current"] += 1
            if value["best"] < value["current"]:
                value["best"] = value["current"]
            value["date"] = str(date)
            prog.value = json.dumps(value)
            prog.save()
            answer["bet"] = bet
            answer["current"] = value["current"]
            answer["best"] = value["best"]
            coins = bet * value["current"] * multiplier
            answer["coins"] = coins
            answer["tomorrowCoins"] = bet * (value["current"] + 1) * multiplier
            answer["tomorrowMultiplier"] = (value["current"] + 1) * multiplier
            answer["subscriptionShow"] = not has_access_content
            answer["subscriptionCoins"] = bet * (value["current"] + 1) * subscription_multiplier
            answer["subscriptionMultiplier"] = (value["current"] + 1) * subscription_multiplier
            user.coins += coins
            user.save()
        elif date == v_date:
            return answer, ""
        else:
            value["current"] = 1
            value["date"] = str(date)
            prog.value = json.dumps(value)
            prog.save()
            answer["current"] = value["current"]
            answer["best"] = value["best"]
            coins = bet * value["current"] * multiplier
            answer["bet"] = bet
            answer["coins"] = coins
            answer["tomorrowCoins"] = bet * (value["current"] + 1) * multiplier
            answer["tomorrowMultiplier"] = (value["current"] + 1) * multiplier
            answer["subscriptionShow"] = not has_access_content
            answer["subscriptionCoins"] = bet * (value["current"] + 1) * subscription_multiplier
            answer["subscriptionMultiplier"] = (value["current"] + 1) * subscription_multiplier
            user.coins += coins
            user.save()
            return answer, ""
    #value = json.loads(prog.value)
    achs = Achievement.objects.filter(category="Вступление в ряды")
    # print("GET ALL ACHS")

    new_ach = dict()
    for ach in achs:
        if answer["current"] >= ach.value:
            obj, create = UserAchievementRelation.objects.get_or_create(user=user, achieve=ach)
            if create:
                user.coins += ach.coins
                user.save()
                new_ach["name"] = ach.name
                new_ach["description"] = ach.description
    # print("AFTER ACHS")
    return answer, new_ach


def get_yesterday_progress(user):
    yesterday = (datetime.datetime.utcnow() - timezone.timedelta(hours=24)).date()
    queryset = AnswersProgressState.objects.filter(
        user=user,
        date=yesterday
    )
    answer = dict()
    if queryset.exists():
        user_progress = queryset.first()
        percent = user_progress.top_percent
        if percent <= 70:
            answer["percent"] = percent
            answer["rightAnswers"] = user_progress.right_answers_per_day
    return answer


def checker_update_enters():
    queryset = InitLog.objects.filter(user__id=21).reverse()  # 2
    ans = []  # [{"t": item.timestamp} for item in queryset]#[{"len": len(queryset), "user": queryset[0].user.id}]
    # return ans
    for item in queryset:
        # ans.append({"a": item.user.id, "d": item.timestamp.date()})
        a, b = update_enters(item.user, item.timestamp.date())
        ans.append({"a": a, "b": b, "date": item.timestamp.date()})
    return ans


def total_update_enters():
    queryset = InitLog.objects.all().order_by('timestamp')  # 2
    # queryset = InitLog.objects.filter(user__id__lt=300).order_by('timestamp')  # 2
    # ans = []#[{"t": item.timestamp} for item in queryset]  # [{"len": len(queryset), "user": queryset[0].user.id}]
    for item in queryset:
        a, b = update_enters(item.user, item.timestamp.date())
        # ans.append({"a": a, "b": b, "date": item.timestamp.date()})
    return "ok"


WEEK_NAMES = [
    "ТОП-50 недели",
    "ТОП-10 недели",
    "ТОП-3 недели",
    "Победитель недельного турнира"
]

WEEK_BEST_PLACE_METRIC = "week_bp"


def update_achievement_rating(user, result, period="week"):
    if period == "week":
        achievements = Achievement.objects.filter(category="Большой турнир", name__in=WEEK_NAMES)  # Change to names
    else:  # period == "month":
        achievements = Achievement.objects.filter(category="Большой турнир")
    new_ach = dict()
    min_result = -1
    for ach in achievements:
        if result <= ach.value:
            min_result = min(min_result, ach.value) if min_result > 0 else ach.value
            item, create = UserAchievementRelation.objects.get_or_create(user=user, achieve=ach)
            if create:
                user.coins += ach.coins
                user.save()
                new_ach["name"] = ach.name
                new_ach["description"] = ach.description
    new_ach['top_n'] = min_result

    return new_ach


def get_week_best_place_user(user):
    metrics = UserMetric.objects.filter(user=user, metric=WEEK_BEST_PLACE_METRIC)
    if metrics.exists():
        metric = metrics.first()
        return int(metric.value)
    return -1


def update_best_week_place_user(user, new_place):
    metrics = UserMetric.objects.filter(user=user, metric=WEEK_BEST_PLACE_METRIC)
    if metrics.exists():
        metric = metrics.first()
        user_value = int(metric.value)
        if user_value > 0 and user_value > new_place:
            metric.value = new_place
            metric.save()
    else:
        metric = UserMetric.objects.create(user=user, metric=WEEK_BEST_PLACE_METRIC)
        metric.value = str(new_place)
        metric.save()


# Функция на один раз, чтобы занести информацию о результатах пользователей в метрики.
def update_best_user_places_in_week_rating():
    achievements = Achievement.objects.filter(category="Большой турнир", name__in=WEEK_NAMES)  # Change to names

    for ach in achievements:
        value = ach.value
        queryset = UserAchievementRelation.objects.filter(achieve=ach)
        for relation in queryset:
            user = relation.user
            update_best_week_place_user(user, value)
        #     break
        # break


def successful_products_p3(user):
    products = ProductLog.objects.filter(product__lesson_type=LESSON_TYPES.P3_AUTOGENERATED_TRAINER_LESSON, user=user)
    value = 0
    for product in products:
        if product.solved_percentage == 100:
            value += 1
    return value


def successful_products_p2(user):
    products = ProductLog.objects.filter(product__lesson_type=LESSON_TYPES.P2_HANDCRAFTED_TRAINER_LESSON, user=user)
    value = 0
    for product in products:
        if product.solved_percentage == 100:
            value += 1
    return value


def successful_blocks(user):
    blocks = TrainerBlockProgress.objects.filter(user=user)
    value = 0
    for block in blocks:
        value += block.successful_attempts
    return value


def num_cards(user):
    blocks = TrainerBlockProgress.objects.filter(user=user, trainer_block__tags__in="maps")
    value = 0
    for block in blocks:
        value += block.attempts
    return value


def num_associate(user):
    return Associate.objects.filter(user=user).count()


def update_other_achievements(user, metric, category, count=1):
    prog, created = UserMetric.objects.get_or_create(metric=metric, user=user)
    answer = dict()
    count = int(count)
    if created:
        answer["current"] = count
        prog.value = str(count)
        prog.save()
    else:
        answer["current"] = int(prog.value) + count
        prog.value = str(int(prog.value) + count)
        prog.save()
    #value = json.loads(prog.value)
    achs = Achievement.objects.filter(category=category)

    new_ach = dict()
    is_send_one_notification = False
    for ach in achs:
        #print(ach.value)
        if answer["current"] >= ach.value:
            obj, create = UserAchievementRelation.objects.get_or_create(user=user, achieve=ach)
            if create:
                user.coins += ach.coins
                user.save()
                new_ach["name"] = ach.name
                new_ach["description"] = ach.description
                if not is_send_one_notification:
                    is_send_one_notification = True
                    try:
                        send_notification_by_user(
                            user,
                            "Новое достижение!",
                            f"Открыто достижение {ach.name}. Молодец!"
                        )
                    except:
                        pass
    #print(new_ach)
    return new_ach


def update_product_achievements(user, currently_completed, product=None):
    update_other_achievements(user, USER_METRIC.SUCCESS_ANSWERS_AMOUNT,
                              "Да пребудут с тобой знания", currently_completed)
    if product is not None and currently_completed == product.total_blocks:
        if product.lesson_type == LESSON_TYPES.P2_HANDCRAFTED_TRAINER_LESSON:
            update_other_achievements(user, "success_prod_p2", "Мегамозг")
        elif product.lesson_type == LESSON_TYPES.P3_AUTOGENERATED_TRAINER_LESSON:
            update_other_achievements(user, "success_prod_p3", "Грандмастер")
