from django.db import models
from Games.constants import QUESTIONS_CATEGORY, ACTIVE_GAME_STATUS

ACTIVE_GAME_STATUS_CHOICE = [
    (ACTIVE_GAME_STATUS.WAITING_FOR_THE_START, 'Waiting for the start'),
    (ACTIVE_GAME_STATUS.PREPARING, 'Preparing to start'),
    (ACTIVE_GAME_STATUS.IN_PROGRESS, 'Game in progress'),
    (ACTIVE_GAME_STATUS.COMPLETED, 'Completed')
]

QUESTIONS_CATEGORY_CHOICE = [
    (QUESTIONS_CATEGORY.ALL, "All"),
    (QUESTIONS_CATEGORY.ANCIENT_TIMES, "Ancient times"),
    (QUESTIONS_CATEGORY.NEW_TIME, "New time"),
    (QUESTIONS_CATEGORY.MODERNITY, "Modernity"),
]


class DuelUserState(models.Model):
    user = models.ForeignKey('Users.User', on_delete=models.SET_NULL, null=True)
    points = models.IntegerField(default=0)
    question_index = models.IntegerField(default=0)
    rating_changes = models.FloatField(default=0.0)

    def __str__(self):
        return str(self.user) + f" {self.points}"


class DuelsConfiguration(models.Model):
    status = models.IntegerField(choices=[
        (0, 'Off'),
        (1, 'On'),
    ], default=1)
    description = models.TextField(null=True, blank=True)


class DuelTrainerBlockRelation(models.Model):
    active_duel = models.ForeignKey('Games.ActiveDuel', on_delete=models.CASCADE, null=True)
    trainer_block = models.ForeignKey('Content.TrainerBlock', on_delete=models.CASCADE, null=True)


class ActiveDuel(models.Model):
    creator = models.ForeignKey('Games.DuelUserState', related_name='creator_active_duel',
                                on_delete=models.SET_NULL, null=True)
    opponent = models.ForeignKey('Games.DuelUserState', related_name='opponent_active_duel',
                                 on_delete=models.SET_NULL, null=True, blank=True)

    status = models.IntegerField(choices=ACTIVE_GAME_STATUS_CHOICE, default=ACTIVE_GAME_STATUS.WAITING_FOR_THE_START)
    is_automatic = models.IntegerField(default=0)  # is this game with computer
    timestamp_create = models.DateTimeField(auto_now_add=True)
    timestamp_start = models.DateTimeField(null=True, blank=True)

    duration = models.IntegerField(verbose_name="Duration in seconds")
    bet = models.IntegerField(verbose_name="Bet")  # ставка
    questions_category = models.IntegerField(choices=QUESTIONS_CATEGORY_CHOICE)

    trainer_blocks = models.ManyToManyField(
        'Content.TrainerBlock',
        through='Games.DuelTrainerBlockRelation',
        related_name='trainer_blocks',
        blank=True,
    )

    class Meta:
        ordering = ['timestamp_create']

    def __str__(self):
        return f"{str(self.creator)} vs {str(self.opponent)}"


class CompletedDuel(models.Model):
    creator = models.ForeignKey('Games.DuelUserState', related_name='creator_completed_duel',
                                on_delete=models.SET_NULL, null=True)
    opponent = models.ForeignKey('Games.DuelUserState', related_name='opponent_completed_duel',
                                 on_delete=models.SET_NULL, null=True)
    timestamp_create = models.DateTimeField()
    timestamp_end = models.DateTimeField(auto_now_add=True)

    is_automatic = models.IntegerField()  # is this game with computer

    duration = models.IntegerField(verbose_name="Duration in seconds")
    bet = models.IntegerField(verbose_name="Bet")  # ставка
    questions_category = models.IntegerField(choices=QUESTIONS_CATEGORY_CHOICE)
