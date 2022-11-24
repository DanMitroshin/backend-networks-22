import json

from Content.models import ContentDialog, ContentDialogAnswer
from django.db.models import Max
from django.utils import timezone
from Content.constants import DIALOG_CATEGORY
from Statistics.models import InitLog, TrainerBlockProgress, ProductLog, ActivityLog, UserMetric
from datetime import timedelta
from collections import Counter
import string
import random

from Users.utils.permissions import check_has_content_access
from Users.constants import DEVICES

FROM_USER = 'fromUser'
MESSAGE = 'message'


BIRTHDAY_DIALOG = [
    {
        'fromUser': False,
        'message': 'Здравствуй, товарищ!'
    },
    {
        'fromUser': False,
        'message': "Уж не знаю, празднуешь ли ты День Рождения, но в любом случае я тебя поздравляю!"
    },
    {
        'fromUser': True,
        'message': "Спасибо!"
    },
    {
        'fromUser': False,
        'message': "Желаю крепкого здоровья и достижения поставленных целей 💯"
    },
    {
        'fromUser': False,
        'message': "Мы всей командой верим, что ты не только сможешь всю нужную историю выучить, "
                   "но и свою идеологию продвигать на весь мир, если потребуется 😎"
    },
    {
        'fromUser': False,
        'message': "В общем, больших тебе побед и успехов 🚀"
    },
    {
        'fromUser': True,
        'message': "Благодарю!"
    },
]


def add_dialog(person_name="", index=None, image='', content=None, author='', save_status=0, category=6):
    if index is None:
        if len(ContentDialog.objects.all()):
            index = ContentDialog.objects.all().aggregate(Max('index'))['index__max'] + 1
        else:
            index = 1

    # content = ADVERTISEMENT_DIALOG_3

    str_content = json.dumps(content)
    print(str_content)
    return
    # print("CATEG", category, person_name, image)

    try:
        ContentDialog.objects.create(
            index=index,
            person_name=person_name,
            image=image,
            content=str_content,
            author=author,
            save_status=int(save_status),
            category=int(category),
        )
    except Exception as e:
        print("ERR", e)


# def get_day_word

def create_yearly_dialog_for_user(user):
    dialog = [
        {
            FROM_USER: False,
            MESSAGE: "Здравствуйте, дорогие россияне!"
        },
        {
            FROM_USER: False,
            MESSAGE: "Кхм, согласен, слишком официально. Все-таки я не в телевузере, или как там он у вас называется. "
                     "Привет, в общем 😉"
        },
        {
            FROM_USER: True,
            MESSAGE: "Привет!"
        },
        {
            FROM_USER: False,
            MESSAGE: "Разработчики попросили меня немножко рассказать тебе о том, "
                     "какой у нас с тобой получился этот год!"
        },
        {
            FROM_USER: True,
            MESSAGE: "Погнали!"
        },
        {
            FROM_USER: False,
            MESSAGE: "Погнали!"
        },
    ]

    days_with_us = min(365, (timezone.now() - user.date_joined).days)
    if days_with_us > 50:
        dialog += [
            {
                FROM_USER: False,
                MESSAGE: f"Сколько дней ты уже с нами? <b>Целых {days_with_us}!</b>"
            },
            {
                FROM_USER: False,
                MESSAGE: f"ОГО 😎\nЯ очень рад, что у нас есть такие пользователи! "
                         f"Надеюсь, в новом году ты продолжишь эту традицию 😉"
            },
            {
                FROM_USER: True,
                MESSAGE: f"О да"
            },
        ]
    else:
        dialog += [
            {
                FROM_USER: False,
                MESSAGE: f"Знаешь, сколько дней ты уже с нами? <b>Целых {days_with_us}!</b>"
            },
            {
                FROM_USER: False,
                MESSAGE: f"Думаю, мы легко пробьем эту планку в новом году 😉"
            },
            {
                FROM_USER: True,
                MESSAGE: f"Конечно!"
            },
        ]

    enters_amount = InitLog.objects.filter(user=user).count()
    dialog += [
        {
            FROM_USER: False,
            MESSAGE: f"У тебя более {enters_amount} использований приложения за этот год!\n"
                     f"🔥 И вот что у тебя получилось сделать за это время:"
        }
    ]

    achievements_amount = 0

    answers_queryset = TrainerBlockProgress.objects.filter(user=user)
    total_answers = 0
    right_answers = 0

    for answer in answers_queryset:
        total_answers += answer.attempts
        right_answers += answer.successful_attempts

    if total_answers >= 10 and right_answers > 5:
        achievements_amount += 1
        dialog += [
            {
                FROM_USER: False,
                MESSAGE: f'🚀 Тобой пройден путь из {total_answers} ответов, среди которых {right_answers} верных!'
            }
        ]
        if total_answers == right_answers:
            dialog += [{
                FROM_USER: False,
                MESSAGE: "Все верные, вот это ты молодец!"
            }]
        elif total_answers * 0.9 < right_answers:
            dialog += [{
                FROM_USER: False,
                MESSAGE: "Почти все верные, молодец!"
            }]
    elif total_answers > 0 and right_answers > 0:
        achievements_amount += 1
        dialog += [{
            FROM_USER: False,
            MESSAGE: f'🚀 У тебя {total_answers} ответов на вопросы, и еще есть куда расти!'
        }]
    else:
        dialog += [{
            FROM_USER: False,
            MESSAGE: f'🚀 У тебя еще не получилось попробовать наши тематические вопросы, '
                     f'так что в новом году будет что-то новое!'
        }]

    product_log_queryset = ProductLog.objects.filter(user=user)
    tests_amount = 0
    theory_amount = 0
    tests_time = timedelta(seconds=0)
    theory_time = timedelta(seconds=0)
    themes = Counter()
    for product in product_log_queryset:
        if product.product.lesson_type == 'p1':
            theory_time += product.time_to_complete
            theory_amount += 1
        if product.product.lesson_type in ['p2', 'p3']:
            tests_time += product.time_to_complete
            tests_amount += 1

        try:
            themes[product.product.content_theme.name] += 1
        except:
            pass

    tests_time = max(2, int(tests_time.total_seconds()) // 60)
    theory_time = max(2, int(theory_time.total_seconds()) // 60)
    # print("TIME", tests_time.total_seconds(), theory_time.total_seconds(), theory_amount)

    best_theme = ''
    best_amount_theme = 0
    for key in themes.keys():
        if themes[key] > best_amount_theme:
            best_amount_theme = themes[key]
            best_theme = key

    def minutes_word_end(amount):
        if amount % 10 in [0, 5, 6, 7, 8, 9] or (5 <= amount % 100 <= 20):
            return "минут"
        # if amount % 10 in [2, 3, 4]:
        return "минуты"

    if tests_time >= 5:
        dialog += [{
            FROM_USER: False,
            MESSAGE: f'🏆 У тебя пройдено более <b>{tests_amount} тестов</b>. '
                     f'А сколько минут заняли у тебя тренировки? Аж <b>{tests_time}</b>!'
        }]
    else:
        if tests_amount >= 2:
            dialog += [{
                FROM_USER: False,
                MESSAGE: f'🏆 У тебя пройдено более <b>{tests_amount} тестов</b>. '
                         f'А все тренировки заняли пока менее 5 минут.'
            }]
        else:
            dialog += [{
                FROM_USER: False,
                MESSAGE: f'🏆 У тебя пройдено не так много нестов. '
                         f'А все тренировки заняли пока менее 5 минут.'
            }]

    if theory_time >= 5:
        dialog += [{
            FROM_USER: False,
            MESSAGE: f'Прочитано уроков теории: {theory_amount}. '
                     f'И это заняло у тебя <b>{theory_time} {minutes_word_end(theory_time)}</b>!'
        }]
    else:
        if theory_amount >= 2:
            dialog += [{
                FROM_USER: False,
                MESSAGE: f'Прочитано уроков теории: {theory_amount}. '
                         f'А чтение заняло пока менее 5 минут.'
            }]
        # else:
        #     dialog += [{
        #         FROM_USER: False,
        #         MESSAGE: f'🏆 У тебя пройдено не так много нестов. '
        #                  f'А все тренировки заняли пока менее 5 минут.'
        #     }]

    if best_theme:
        dialog += [{
            FROM_USER: False,
            MESSAGE: f'🍵 И да, твоя любимая тема в этом году - это <b>"{best_theme}"</b>'
        }]

    dialog += [{
        FROM_USER: True,
        MESSAGE: f'Отлично!'
    }]

    activities_wiki = len(ActivityLog.objects.filter(user=user, activity__startswith='C_'))

    if activities_wiki >= 7:
        dialog += [{
            FROM_USER: False,
            MESSAGE: f'А еще, думаю, тебе чем-то понравилась наша внутренняя сеть знаний, '
                     f'ведь у тебя {activities_wiki} ее использований!'
        }]
    else:
        dialog += [{
            FROM_USER: False,
            MESSAGE: f'А еще в будущем году у тебя есть шанс больше изучать нашу сеть знаний, '
                     f'пока что у тебя менее 7 использований. Надеюсь, тебе понравится:)'
        }]

    try:
        week_bp_queryset = UserMetric.objects.filter(user=user, metric='week_bp')
        if week_bp_queryset.exists():
            week_bp = int(week_bp_queryset.first().value)
            dialog += [{
                FROM_USER: False,
                MESSAGE: f'🏆 Ах да, и твое лучшее место в рейтинге - {week_bp}! Продолжай тренироваться и дальше!'
            }]
    except:
        pass

    dialog += [{
        FROM_USER: True,
        MESSAGE: f'Точно!'
    }]

    has_access = check_has_content_access(user)
    if has_access:
        dialog += [
            {
                FROM_USER: False,
                MESSAGE: f'И спасибо тебе, что ты с нами 😎\nМы очень благодарны тебе за доверие и будем стараться '
                         f'делать для тебя всё лучшее и дальше! С праздниками тебя!'
            },
            {
                FROM_USER: True,
                MESSAGE: "Спасибо!"
            }
        ]
    else:
        dialog += [
            {
                FROM_USER: False,
                MESSAGE: f'И спасибо тебе, что ты с нами 😎\nМы благодарны тебе за доверие и '
                         f'к новому году хотим сделать небольшой подарок!'
            },
            {
                FROM_USER: False,
                MESSAGE: f'Даем <b>промокод YEAR_2022</b> на скидку на 3 месяца доступа! Можешь заскринить:)'
            },
            {
                FROM_USER: False,
                MESSAGE: f'❗ Он будет действовать только несколько дней. '
                         f'Так что если ты хочешь получить полный доступ, сейчас самое время 😌'
            },
            {
                FROM_USER: False,
                MESSAGE: f'С праздниками тебя! И больших успехов в изучении истории!'
            },
            {
                FROM_USER: True,
                MESSAGE: "Спасибо!"
            }
        ]

    return dialog


def get_first_promo_code(amount=4):
    letters = string.ascii_lowercase + string.ascii_uppercase + '0123456789'
    rand_string = ''.join(random.choice(letters) for _ in range(amount))
    return f'HIST_{rand_string}'


def get_first_promo_code_to_user(user):
    return ""


def get_dialog(index, user=None, show_author=False):
    dialog = ContentDialog.objects.filter(index=index).first()
    dialog_dict = {
        'dialog': json.loads(dialog.content), # if user.username not in ['vk__103159559', 'vk__133671258'] else FIRST_ENTER_CONTENT,
        'saveChoices': bool(dialog.save_status),
        'index': dialog.index,
        'name': dialog.person_name,
    }
    if dialog.image:
        dialog_dict['image'] = dialog.image
    if dialog.author and show_author:
        dialog_dict['author'] = dialog.author

    if dialog.category == DIALOG_CATEGORY.YEARLY_DIALOG:
        yearly_dialog = create_yearly_dialog_for_user(user)
        dialog_dict['dialog'] = yearly_dialog

    elif dialog.category == DIALOG_CATEGORY.FIRST_ENTER:

        try:
            if user.device != DEVICES.APPLE and random.random() < 0.99:
                code = get_first_promo_code_to_user(user)
            else:
                del dialog_dict['dialog'][-3:-1]
        except:
            code = 'SECRET_CODE_6548'
        # print("GET CODE:", code)

        # for message_data in dialog_dict['dialog']:
        #     message_data[MESSAGE] = message_data[MESSAGE].replace('{promo_code}', code)

    elif dialog.category == DIALOG_CATEGORY.BIRTHDAY_DIALOG:
        if (not check_has_content_access(user)) and (user.device != DEVICES.APPLE):
            code = get_first_promo_code_to_user(user)
            dialog_dict['dialog'] += [
                {
                    FROM_USER: False,
                    MESSAGE: "Кстати. Я, конечно, не Санта, но небольшой подарок в виде промокода "
                             "уже ждет тебя в твоем профиле!"
                },
                {
                    FROM_USER: True,
                    MESSAGE: "Огонь!"
                }
            ]

    return dialog_dict


def save_user_dialog_choices(user, dialog_index, actions):
    for action in actions:
        ContentDialogAnswer.objects.create(
            user=user,
            dialog_index=dialog_index,
            action_index=action,
        )


def get_dialog_impressions_amount(index):
    return ContentDialogAnswer.objects.filter(dialog_index=index).count()


def get_action_with_dialog_info(index, impressions_amount, action_number):
    actions_amount = ContentDialogAnswer.objects.filter(dialog_index=index, action_index=action_number).count()
    if impressions_amount > 0:
        return f"{actions_amount} ({round(actions_amount / impressions_amount * 100, 1)}%)"
    return f"0 (0%)"


def get_good_actions_with_dialog_info(index, impressions_amount, action_number=2):
    return get_action_with_dialog_info(index, impressions_amount, action_number)


def get_bad_actions_with_dialog_info(index, impressions_amount, action_number=1):
    return get_action_with_dialog_info(index, impressions_amount, action_number)


def get_statistics_answers_dialog(dialog_index):
    all_answers = ContentDialogAnswer.objects.filter(dialog_index=dialog_index)
    stat_dict = Counter()
    counter = 0
    for answer in all_answers:
        counter += 1
        stat_dict[answer.action_index] += 1
    good_answer = 2
    close_answer = 1
    text = f"Всего показов: {counter}\n"
    if counter > 0:
        text += f"Переходов по ссылке: {stat_dict[good_answer]} ({round(stat_dict[good_answer] / counter * 100, 1)}%)\n"
        text += f"Отказов: {stat_dict[close_answer]} ({round(stat_dict[close_answer] / counter * 100, 1)}%)"
    return text
