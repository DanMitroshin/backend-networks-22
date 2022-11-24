from django.db import models
from django.db.models.constraints import UniqueConstraint
# from django.contrib.postgres.fields import JSONField

from datetime import timedelta
from Statistics.constants import QUESTION_PROBLEMS


QUESTION_PROBLEMS_CHOICE = [
    (QUESTION_PROBLEMS.ERRORS_IN_QUESTION, 'Errors in question'),
    (QUESTION_PROBLEMS.BAD_THEME, 'Unsuitable test theme for question'),
    (QUESTION_PROBLEMS.QUESTION_REPEAT, 'This question repeats in test'),
    (QUESTION_PROBLEMS.NEW_ANSWER_SUGGESTION, 'Suggestion of new answer'),

    (QUESTION_PROBLEMS.OTHER, 'Other problems'),
]


class Achievement(models.Model):
    category = models.TextField(verbose_name='achievement type')
    value = models.IntegerField(verbose_name='value')
    name = models.CharField(verbose_name='name', max_length=100)
    description = models.TextField(verbose_name='description', blank=True)
    coins = models.IntegerField(default=0)


class UserMetric(models.Model):
    user = models.ForeignKey('Users.User', on_delete=models.CASCADE, null=True)
    value = models.TextField(verbose_name="value", default="0")
    metric = models.TextField(verbose_name='metric')

    class Meta:
        constraints = [UniqueConstraint(fields=['user', 'metric'], name='user_metric_unique')]


class ActivityLog(models.Model):
    user = models.ForeignKey('Users.User', on_delete=models.SET_NULL, null=True)
    activity = models.CharField(verbose_name='activity type', max_length=20)
    payload = models.TextField(verbose_name='activity payload, if provided', blank=True, null=True)
    timestamp = models.DateField(verbose_name='timestamp', auto_now_add=True)


class TrainerBlockLog(models.Model):
    user = models.ForeignKey('Users.User', on_delete=models.CASCADE)
    trainer_block = models.ForeignKey('Content.TrainerBlock', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(verbose_name='timestamp', auto_now_add=True)
    is_valid = models.BooleanField(verbose_name='is answer valid', default=False)
    answer = models.CharField(verbose_name='answer', blank=True, max_length=100)


class AnswersProgressState(models.Model):
    user = models.ForeignKey('Users.User', on_delete=models.CASCADE)
    date = models.DateField(verbose_name='Day of state')
    total_answers = models.IntegerField(verbose_name="Total amount of answers")
    total_right_answers = models.IntegerField(verbose_name="Total amount of right answers")
    answers_per_day = models.IntegerField(verbose_name="Amount of answers per day")
    right_answers_per_day = models.IntegerField(verbose_name="Amount of right answers per day")
    top_percent = models.IntegerField(
        verbose_name="Top percent of user among other results this day",
        blank=True,
        null=True
    )


class TrainerBlockProgress(models.Model):
    class Meta:
        indexes = [models.Index(fields=['user', 'trainer_block']), ]
        constraints = [UniqueConstraint(fields=['user', 'trainer_block'], name='unique_pair')]
        ordering = ['balance']

    user = models.ForeignKey('Users.User', on_delete=models.CASCADE)
    trainer_block = models.ForeignKey('Content.TrainerBlock', on_delete=models.CASCADE)
    attempts = models.IntegerField(default=0)
    successful_attempts = models.IntegerField(default=0)
    balance = models.IntegerField(default=0)

    def update_balance(self):
        self.balance = self.successful_attempts * 2 - self.attempts
        return self.balance

    def save(self, *args, **kwargs):
        self.update_balance()
        super().save(*args, **kwargs)

    def add_successful_attempt(self):
        self.attempts += 1
        self.successful_attempts += 1

    def add_unsuccessful_attempt(self):
        self.attempts += 1

    def add_answer(self, is_valid):
        if is_valid:
            self.add_successful_attempt()
        else:
            self.add_unsuccessful_attempt()
        self.save()

    @property
    def success_rate(self):
        return (self.successful_attempts / self.attempts) if self.attempts != 0 else 0


class ProductProgress(models.Model):
    class Meta:
        indexes = [models.Index(fields=['user', 'product']), ]
        constraints = [UniqueConstraint(fields=['user', 'product'], name='unique_product')]

    user = models.ForeignKey('Users.User', on_delete=models.CASCADE)
    product = models.ForeignKey('Content.Product', on_delete=models.CASCADE, related_name='progress')
    completed = models.IntegerField(verbose_name='number of completed blocks', default=0)

    @property
    def progress(self):
        if self.product.total_blocks > 0:
            return min(100, int(100 * self.completed / self.product.total_blocks))
        else:
            return 0


class ProductLog(models.Model):
    user = models.ForeignKey('Users.User', on_delete=models.CASCADE)
    product = models.ForeignKey('Content.Product', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(verbose_name='timestamp', auto_now_add=True)
    time_to_complete = models.DurationField(
        verbose_name='Product completion time',
        default=timedelta(seconds=0)
    )
    completed = models.IntegerField(verbose_name='number of completed blocks', default=0)

    @property
    def solved_percentage(self):
        if self.product.total_blocks > 0:
            return int(100 * self.completed / self.product.total_blocks)
        else:
            return 0


class GenerateLog(models.Model):
    user = models.ForeignKey('Users.User', on_delete=models.CASCADE)
    text = models.TextField(verbose_name='date')
    timestamp = models.DateTimeField(verbose_name='timestamp', auto_now_add=True)
    amount = models.IntegerField(verbose_name='amount')


class InitLog(models.Model):
    user = models.ForeignKey('Users.User', on_delete=models.CASCADE)
    title = models.TextField(verbose_name='title')
    timestamp = models.DateTimeField(verbose_name='timestamp', auto_now_add=True)
    version = models.IntegerField(verbose_name='version')
    device = models.CharField(verbose_name="current_device", max_length=10, default="a")


class MetricsCache(models.Model):
    value = models.TextField()
    day = models.DateField()
    average = models.FloatField(default=0, blank=True, null=True)
    metric = models.CharField(max_length=150, blank=True, null=True)


class WeekRating(models.Model):
    user = models.ForeignKey('Users.User', on_delete=models.CASCADE)
    value = models.IntegerField(verbose_name='value')
    status = models.IntegerField(verbose_name='status')
    best_place = models.IntegerField(verbose_name='best_place', null=True, blank=True)

    class Meta:
        ordering = ['-value']


class UserAnswerForReview(models.Model):
    user = models.ForeignKey('Users.User', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(verbose_name='Timestamp', blank=True, null=True)
    question = models.ForeignKey('Content.TrainerBlock', on_delete=models.CASCADE)
    problem = models.IntegerField(verbose_name="Problem", choices=QUESTION_PROBLEMS_CHOICE, blank=True, null=True)
    answer = models.TextField(verbose_name="User answer")
    comment = models.TextField(verbose_name="User comment", blank=True, null=True)
    status = models.IntegerField(
        verbose_name="Status of review",
        choices=[
            (0, "Waiting for review"),
            (1, "Accepted"),
            (2, "Rejected"),
        ],
        default=0
    )
