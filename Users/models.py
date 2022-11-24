import re

from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework.exceptions import ValidationError
from django.db.models.constraints import UniqueConstraint

from .constants import ACCESS_GROUP_ROLES
# import Users.constants.devices as DEVICES
from Users.constants import DEVICES
from .constants import REGISTRATION_PLATFORMS, USER_SEX


REGISTRATION_PLATFORM_CHOICES = [
    (REGISTRATION_PLATFORMS.EMAIL, 'Email'),
    (REGISTRATION_PLATFORMS.VK, 'VK'),
    (REGISTRATION_PLATFORMS.APPLE_ID, 'Apple ID')
]

DEVICE_CHOICES = [
    (DEVICES.ANDROID, 'Android'),
    (DEVICES.APPLE, 'Apple'),
    (DEVICES.WEB, 'Web')
]

USER_SEX_CHOICES = [
    (USER_SEX.UNKNOWN, "Unknown"),
    (USER_SEX.WOMAN, 'Woman'),
    (USER_SEX.MAN, 'Man'),
]


class AccessGroupUserRelation(models.Model):
    user = models.ForeignKey('Users.User', on_delete=models.CASCADE)
    access_group = models.ForeignKey('Content.AccessGroup', on_delete=models.CASCADE)
    expires_at = models.DateTimeField(null=True, blank=True)
    role = models.CharField(max_length=32, choices=ACCESS_GROUP_ROLES, default='access_permanent')


class UserAchievementRelation(models.Model):
    user = models.ForeignKey('Users.User', on_delete=models.SET_NULL, null=True)
    achieve = models.ForeignKey('Statistics.Achievement', on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(verbose_name='timestamp', auto_now_add=True)


class User(AbstractUser):
    vk_id = models.CharField(max_length=20, blank=True, null=True, unique=True)
    vk_access_token = models.CharField(max_length=400, blank=True)

    identifier = models.UUIDField(editable=True, unique=True, null=True, blank=True)
    account_token = models.CharField(max_length=100, unique=True, null=True, blank=True)

    nickname = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
        help_text="Nickname must be between 5 and 100 letters long can't match 'id[0-9]+'",
    )
    registration_platform = models.IntegerField(
        choices=REGISTRATION_PLATFORM_CHOICES,
        default=REGISTRATION_PLATFORMS.EMAIL,
    )
    device = models.IntegerField(
        choices=DEVICE_CHOICES,
        default=DEVICES.ANDROID,
    )
    last_entry = models.DateTimeField(verbose_name='last entry', blank=True, null=True)
    version_app = models.IntegerField(default=-1, verbose_name="User's app version")
    is_teacher = models.BooleanField(
        default=False,
        verbose_name='Teacher status',
        help_text='Designates whether the user is a teacher.',
    )

    image = models.URLField(max_length=250, null=True, blank=True)
    image_50 = models.URLField(max_length=250, null=True, blank=True)
    sex = models.PositiveSmallIntegerField(choices=USER_SEX_CHOICES, null=True, blank=True)

    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    educational_institution = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    coins = models.IntegerField(default=400)
    rating_stars = models.FloatField(default=800.0)

    access_groups = models.ManyToManyField(
        'Content.AccessGroup',
        through='Users.AccessGroupUserRelation',
        related_name='users',
    )

    achievements = models.ManyToManyField(
        'Statistics.Achievement',
        through='Users.UserAchievementRelation',
        related_name='achievements',
    )

    class Meta:
        indexes = [models.Index(fields=['username', 'vk_id']), ]
        constraints = [UniqueConstraint(fields=['username', 'vk_id'], name='username_vk_id_unique')]

    def save(self, *args, **kwargs):
        if not self.vk_id:
            self.vk_id = None
        if not self.nickname or f'id{self.id}' == self.nickname:
            self.nickname = None
        if self.nickname is not None:
            self.validate_nickname()
        super(User, self).save(*args, **kwargs)

    def get_nickname(self):
        return f'id{self.id}' if self.nickname is None else self.nickname

    def validate_nickname(self):
        if re.fullmatch(r'id[0-9]+', self.nickname):
            raise ValidationError(
                {'nickname': [{"en": "nickname can't be in formatted like 'id{number}'",
                               "ru": "Никнейм не может иметь формат 'id{число}'"
                               }]}
            )
        elif len(self.nickname) <= 4:
            raise ValidationError(
                {'nickname': [{"en": "nickname can't be shorter than 5 letters",
                               "ru": "Никнейм не может быть короче 5 символов"
                               }]}
            )


class NotificationPushToken(models.Model):
    user = models.ForeignKey('Users.User', on_delete=models.CASCADE, null=True)
    token = models.TextField(unique=True)
    type = models.CharField(max_length=10)
    active = models.IntegerField(default=1)

    class Meta:
        indexes = [models.Index(fields=['user', 'token']), ]


class BannedUser(models.Model):
    user = models.ForeignKey('Users.User', on_delete=models.CASCADE, null=True)
    type = models.IntegerField(verbose_name='Type of ban')
    end_day = models.DateField(verbose_name='End day')
    description = models.TextField(blank=True)


class UserInfoVersion(models.Model):
    user = models.ForeignKey('Users.User', on_delete=models.CASCADE)
    app_version = models.IntegerField(verbose_name='App version')
    dialog_version = models.IntegerField(verbose_name='Dialog version')
    advertisement_version = models.IntegerField(verbose_name='Advertisement version', default=0)
    last_dialog_time = models.DateTimeField(verbose_name='Timestamp of last sending dialog')
    notification_version = models.IntegerField(verbose_name='Notification version')
    motivation_version = models.IntegerField(verbose_name='Motivation version', default=0)
    sale_content_version = models.IntegerField(verbose_name='Sale content dialog version', default=0)
