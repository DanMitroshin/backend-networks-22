from Content.models import ContentDialog
from Content.constants import DIALOG_CATEGORY, DIALOG_STATUS
from django.db.models import Max, Min
from Users.models import UserInfoVersion
import datetime


def get_last_dialog_index_after_update_app():
    try:
        max_index = ContentDialog.objects.filter(category=DIALOG_CATEGORY.AFTER_UPDATE_APP).aggregate(Max('index'))
        return int(max_index['index__max'])
    except:
        return 1


def get_dialog_index_about_update_for_app_version(app_version):
    try:
        return ContentDialog.objects.filter(category=DIALOG_CATEGORY.AFTER_UPDATE_APP, app_version=app_version).first().index
    except:
        return 0


def get_first_enter_dialog_index():
    return ContentDialog.objects.filter(category=DIALOG_CATEGORY.FIRST_ENTER).first().index


def get_max_dialog_index_by_category(category):
    try:
        max_index = ContentDialog.objects.filter(category=category).aggregate(
            Max('index'))['index__max']
        if not max_index:
            max_index = 0
    except:
        max_index = 0
    return max_index


def get_next_dialog_index_by_category(category, current_index):
    try:
        min_index = ContentDialog.objects.filter(
            category=category,
            index__gt=current_index,
            status=DIALOG_STATUS.ACTIVE,
        ).aggregate(
            Min('index'))['index__min']
        if not min_index:
            min_index = 0
    except:
        min_index = 0
    return min_index


def get_max_information_dialog_index():
    return get_max_dialog_index_by_category(DIALOG_CATEGORY.INFORMATION)


def get_max_advertisement_dialog_index():
    return get_max_dialog_index_by_category(DIALOG_CATEGORY.ADVERTISEMENT)


def get_next_advertisement_dialog_index(current_index):
    return get_next_dialog_index_by_category(DIALOG_CATEGORY.ADVERTISEMENT, current_index)


def get_next_motivation_dialog_index(current_index):
    return get_next_dialog_index_by_category(DIALOG_CATEGORY.MOTIVATION, current_index)


def get_next_sale_content_dialog_index(current_index):
    return get_next_dialog_index_by_category(DIALOG_CATEGORY.SALE_CONTENT, current_index)


def get_congratulations_new_year_dialog_index():
    return get_max_dialog_index_by_category(DIALOG_CATEGORY.YEARLY_DIALOG)


def get_birthday_dialog_index():
    return get_max_dialog_index_by_category(DIALOG_CATEGORY.BIRTHDAY_DIALOG)


def get_dialog_index_for_user(user, app_version, amount_inits):
    info_queryset = UserInfoVersion.objects.filter(user=user)
    max_info_index = get_max_information_dialog_index()
    if not info_queryset.exists():
        info = UserInfoVersion.objects.create(
            user=user,
            dialog_version=max_info_index,
            notification_version=1,
            last_dialog_time=datetime.datetime.now(),
            app_version=1
        )
    else:
        info = info_queryset.first()

    # FIRST ENTER
    if app_version > 0 and amount_inits <= 1:
        info.app_version = app_version
        info.save()
        return get_first_enter_dialog_index()

    current_advertisement_version = info.advertisement_version
    advertisement_max_index = get_next_advertisement_dialog_index(current_advertisement_version)

    if current_advertisement_version < advertisement_max_index:
        info.advertisement_version = advertisement_max_index
        info.save()
        return advertisement_max_index

    return None
