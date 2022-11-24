from django.db import models

from Content.constants import ACCESS_GROUP_TYPES
# from Content.utils import generate_invite_code


class AccessGroup(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=32, choices=ACCESS_GROUP_TYPES, default='access')
    invite_code = models.CharField(
        max_length=32,
        unique=True,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f'{self.name} [{self.type}]'
