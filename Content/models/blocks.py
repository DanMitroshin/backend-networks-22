from django.db import models
import json
from Content.constants import QUESTION_TYPES

QUESTION_TYPE_CHOICES = [
    (QUESTION_TYPES.ONE_ANSWER, 'One possible answer'),
    (QUESTION_TYPES.MANY_ANSWERS, 'Many possible answers'),
    (QUESTION_TYPES.MANUALLY, 'Answer should be typed in'),
    (QUESTION_TYPES.CHRONOLOGICAL, 'Chronological sequence of variants'),
    (QUESTION_TYPES.RELATIONS, 'Relations between variants'),
    (QUESTION_TYPES.REASONS_AND_ARGUMENTS, 'Reasons and arguments')
]


class TrainerBlockTag(models.Model):
    tag = models.CharField(max_length=5, primary_key=True)
    description = models.TextField()

    def __str__(self):
        return f'{self.tag} : {self.description}'


class TrainerBlockPerson(models.Model):
    person = models.CharField(max_length=10)
    description = models.TextField(default="")
    name = models.CharField(max_length=50, default="")

    def __str__(self):
        return self.name


class TrainerBlockPeriod(models.Model):
    period = models.CharField(max_length=10)
    description = models.TextField(default="")
    name = models.CharField(max_length=50, default="")
    persons = models.ManyToManyField(TrainerBlockPerson, blank=True)
    section = models.CharField(max_length=10, blank=True, default='', db_index=True)

    def __str__(self):
        return self.name


class TrainerBlock(models.Model):
    # Displayed information
    question = models.TextField(verbose_name='Text of a question')
    trivia = models.TextField(verbose_name='Trivia for a question', blank=True)
    img = models.TextField(verbose_name='Image for a question', blank=True)
    index = models.IntegerField(verbose_name='Unique index', unique=True, blank=True, null=True)

    # Answers
    answers = models.TextField(verbose_name='List of answers', blank=True)
    valid_answers = models.TextField(verbose_name='List of valid answers', blank=True)

    # Meta
    question_type = models.CharField(
        verbose_name='Type of a question',
        choices=QUESTION_TYPE_CHOICES,
        default='one',
        max_length=5,
    )

    # if active == -2 then this question is special
    active = models.IntegerField(default=1)

    # Taxonomy
    theme = models.CharField(max_length=250, db_index=True, blank=True)
    section = models.CharField(max_length=10, db_index=True, blank=True)

    # Tags
    persons = models.ManyToManyField(
        TrainerBlockPerson,
        verbose_name='persons',
        blank=True
    )
    periods = models.ManyToManyField(
        TrainerBlockPeriod,
        verbose_name='periods',
        blank=True,
    )
    tags = models.ManyToManyField(
        TrainerBlockTag,
        verbose_name='tags',
        blank=True,
        related_name='trainer_blocks'
    )

    @property
    def invalid_answers(self):
        return json.dumps([elem for elem in json.loads(self.answers) if elem not in json.loads(self.valid_answers)],
                          ensure_ascii=False)

    def __str__(self):
        return f"({self.id}) {self.question[:100]}"


class MediaBlock(models.Model):
    name = models.CharField(verbose_name='media block name', max_length=250, blank=True)
    text = models.TextField(verbose_name='media block text')

    def __str__(self):
        return self.name
