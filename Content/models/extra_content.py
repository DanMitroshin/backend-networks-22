from django.db import models

from Content.constants import DIALOG_CATEGORY
from Content.constants import DIALOG_STATUS

DIALOG_STATUS_CHOICES = [
    (DIALOG_STATUS.INACTIVE, "Inactive dialog"),
    (DIALOG_STATUS.ACTIVE, "Active dialog")
]

DIALOG_CATEGORY_CHOICES = [
    (DIALOG_CATEGORY.AFTER_UPDATE_APP, 'About new app update'),
    (DIALOG_CATEGORY.TO_UPDATE_APP, 'Redirect to store to update app'),
    (DIALOG_CATEGORY.FIRST_ENTER, 'First enter'),
    (DIALOG_CATEGORY.MOTIVATION, 'Motivation dialog'),
    (DIALOG_CATEGORY.SALE_CONTENT, 'Sale content'),
    (DIALOG_CATEGORY.INFORMATION, 'Information dialog'),
    (DIALOG_CATEGORY.DAILY_LEARNING, 'Daily learning'),
    (DIALOG_CATEGORY.DAILY_STATISTICS, 'Daily statistics'),
    (DIALOG_CATEGORY.WEEKLY_STATISTICS, 'Weekly statistics'),
    (DIALOG_CATEGORY.MONTHLY_STATISTICS, 'Monthly statistics'),
    (DIALOG_CATEGORY.ADVERTISEMENT, 'Advertisement for projects outside the app'),
    (DIALOG_CATEGORY.FUN_AND_ENTERTAINMENT, 'Fun and entertainment'),
    (DIALOG_CATEGORY.RATING_RESULT, 'Rating results'),
    (DIALOG_CATEGORY.RATING_PARTICIPATE, 'Rating participate'),
    (DIALOG_CATEGORY.RETURN_TO_APP, 'Return to app after break'),
    (DIALOG_CATEGORY.GIFT, 'Gifts and prizes'),
    (DIALOG_CATEGORY.YEARLY_DIALOG, 'Yearly dialog'),
    (DIALOG_CATEGORY.BIRTHDAY_DIALOG, 'Birthday dialog'),
    (DIALOG_CATEGORY.FOR_TEST, 'Test dialog'),
]


class ContentDialog(models.Model):
    index = models.IntegerField(
        verbose_name='Dialog index',
        help_text="Это уникальный индекс диалога (ставится по возрастанию от предыдущих, "
                  "иногда с каким-то зазором в 2-3 свободных индекса).",
        unique=True)
    person_name = models.CharField(max_length=30)
    app_version = models.IntegerField(
        verbose_name='App dialog version about update',
        help_text="Используется, если категория диалога рассчитана на информацию об обновлении.",
        null=True, blank=True)
    image = models.TextField(
        verbose_name='Link to the image of person',
        help_text="Очень желательно, чтобы картинка была скругленной и сжатой, 100 на 100 вполне ок.",
        blank=True)
    content = models.TextField(
        verbose_name='Dialog content',
        help_text="Это JSON-представление диалога. Часто совсем нечитабельное из-за перевода в другую кодировку.",
    )
    author = models.CharField(
        verbose_name='Author of the dialog',
        help_text="Кто придумал диалог. Обычно не указывается, чтобы не отображалось у пользователя.",
        max_length=30, blank=True)
    save_status = models.IntegerField(
        verbose_name='Status for saving user answers',
        help_text="1 - сохранять ответы для статистики, 0 - не сохранять. Обычно 1, если предполагается выбор.",
    )
    category = models.IntegerField(
        verbose_name='Dialog category',
        help_text="Для тестирования используй категорию Test. Ее потом можно заменить.",
        choices=DIALOG_CATEGORY_CHOICES, null=True, blank=True)
    status = models.IntegerField(
        verbose_name='Dialog status',
        help_text="Неактивные диалоги не будут отображаться и учитываться в очереди на отображение для пользователей",
        choices=DIALOG_STATUS_CHOICES, default=DIALOG_STATUS.ACTIVE)

    def __str__(self):
        return f'{self.index}: {self.person_name}'

    def impressions_amount(self):
        return ContentDialogAnswer.objects.filter(dialog_index=self.index).count()

    def get_action_with_dialog_info(self, action_number):
        impressions_amount = self.impressions_amount()
        actions_amount = ContentDialogAnswer.objects.filter(dialog_index=self.index, action_index=action_number).count()
        if impressions_amount > 0:
            return f"{actions_amount} ({round(actions_amount / impressions_amount * 100, 1)}%)"
        return f"0 (0%)"

    def good_actions_with_dialog_info(self):
        return self.get_action_with_dialog_info(2)

    def bad_actions_with_dialog_info(self):
        return self.get_action_with_dialog_info(1)

    impressions_amount.short_description = u'Количество показов'
    good_actions_with_dialog_info.short_description = u'Переходов по ссылке'
    bad_actions_with_dialog_info.short_description = u'Отказов'


class ContentDialogAnswer(models.Model):
    user = models.ForeignKey('Users.User', on_delete=models.CASCADE)
    dialog_index = models.IntegerField(verbose_name='Dialog index')
    action_index = models.IntegerField(verbose_name='User action index')
    timestamp = models.DateTimeField(verbose_name='Timestamp', auto_now_add=True)


class SpecialQuestionAnswer(models.Model):
    question = models.ForeignKey('TrainerBlock', verbose_name="Question", on_delete=models.CASCADE)
    user = models.ForeignKey('Users.User', on_delete=models.CASCADE)
    answer = models.TextField(verbose_name="User answer")
    timestamp = models.DateTimeField(verbose_name='Timestamp', auto_now_add=True)
