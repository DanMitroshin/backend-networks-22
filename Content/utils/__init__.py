from random import sample, shuffle, choices, randint
import time

from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.utils.crypto import get_random_string
from rest_framework.exceptions import PermissionDenied

from Content.models import ContentVideo
from Users.models import User, UserAchievementRelation
from Users.utils.permissions import check_access

from .classroom_actions import get_and_validate_classroom


def generate_invite_code():
    return f'{get_random_string(length=6)}-{get_random_string(length=6)}'


def validate_access(user, product):
    if product.access_groups.exists():
        for access_group in product.access_groups.all():
            if check_access(access_group.name, user):
                return
        raise PermissionDenied(detail='User doesn\'t allowed to view this product', code=None)


def get_video_info(index, access=True):
    video = ContentVideo.objects.filter(index=index)
    if video.exists():
        video = video.first()
        video_src = video.video
        name = video.name if video.name else video_src.name
        image_uri = video.image if video.image else video_src.image
        start = video.time_code
        video_id = video_src.key

        if access:
            return {
                "name": name,
                "start": start,
                "videoId": video_id,
            }
        else:
            return {
                "name": name,
                "uri": image_uri,
            }
    else:
        raise ValueError


def strip_dict_values(d: dict):
    for key, value in d.items():
        if type(value) == str:
            d[key] = value.strip()
    return d


# Функция на один раз при добавлении монет
def update_users_coins():
    User.objects.all().update(coins=400)
    for achievement_relation in UserAchievementRelation.objects.all():
        user = achievement_relation.user
        user.coins += achievement_relation.achieve.coins
        user.save()
