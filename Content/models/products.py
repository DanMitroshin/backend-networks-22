from django.db import models

from Content.constants import PRODUCT_MODEL_LESSON_TYPE_CHOICE, LESSON_TYPES


class ContentTheme(models.Model):
    # Fields
    name = models.CharField(verbose_name='Theme name', max_length=250)
    index = models.IntegerField(verbose_name='Unique index', unique=True, blank=True, null=True)
    description = models.TextField(verbose_name='Description', blank=True)
    video = models.ForeignKey('ContentVideo', on_delete=models.SET_NULL, verbose_name='Video', null=True, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    # Fields
    name = models.CharField(verbose_name='Lesson name', max_length=250)
    index = models.IntegerField(verbose_name='Unique index', unique=True, blank=True, null=True)
    content_theme = models.ForeignKey('ContentTheme', on_delete=models.SET_NULL, null=True, blank=True)
    active = models.IntegerField(default=1)
    trainer_blocks = models.ManyToManyField(
        'TrainerBlock',
        verbose_name='Trainer blocks',
        related_name='trainers',
        blank=True)
    media_blocks = models.ManyToManyField(
        'MediaBlock',
        verbose_name='Media blocks',
        related_name='media',
        blank=True)
    lesson_type = models.CharField(
        verbose_name='Lesson type',
        choices=PRODUCT_MODEL_LESSON_TYPE_CHOICE,
        default=LESSON_TYPES.P2_HANDCRAFTED_TRAINER_LESSON,
        max_length=5
    )
    theme = models.CharField(max_length=250, db_index=True, blank=True)
    section = models.CharField(max_length=10, db_index=True, blank=True)
    tag = models.TextField(blank=True)
    creation_date = models.DateTimeField(auto_now_add=True, null=True)

    access_groups = models.ManyToManyField('Content.AccessGroup', related_name='products', blank=True)

    def __str__(self):
        return self.name

    # Properties
    @property
    def total_blocks(self):
        if self.lesson_type in ['p1']:
            return self.media_blocks.count()
        elif self.lesson_type in ['p2', 'p3']:
            return self.trainer_blocks.count()


class Associate(models.Model):
    associate = models.CharField(verbose_name='associate', max_length=250)
    is_algorithm = models.IntegerField(default=1)
    date = models.CharField(verbose_name="date", max_length=50)
    user = models.ForeignKey('Users.User', on_delete=models.SET_NULL, null=True)
    event = models.TextField(verbose_name='event', blank=True)
    number = models.CharField(verbose_name='number', max_length=100, blank=True)
