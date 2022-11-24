import datetime
import json

from Content.models import TrainerBlock
from Content.serializers import TrainerBlockSerializer
from Games.models import ActiveDuel, CompletedDuel, DuelUserState, DuelsConfiguration
from Statistics.metrics.totals import get_user_rating_name
from Games.constants import QUESTIONS_CATEGORY, ACTIVE_GAME_STATUS
from django.db.models.functions import Length

from time import sleep
from random import choice, shuffle, sample, randint, random
from Content.constants import QUESTION_TYPES
from Statistics.models import TrainerBlockLog, TrainerBlockProgress

from Users.models import User

QUESTIONS_CATEGORY_ARRAY = [
    QUESTIONS_CATEGORY.ALL,
    QUESTIONS_CATEGORY.ANCIENT_TIMES,
    QUESTIONS_CATEGORY.NEW_TIME,
    QUESTIONS_CATEGORY.MODERNITY,
]

CHARGE = 0.2
PROFIT_COEFFICIENT = 0.8

BORDER_SECONDS_AMOUNT_TO_AUTOMATIC = 14
AUTOMATIC_SECONDS_TO_ONE_ANSWER = 6
BOT_ACCOUNT_AMOUNT = 30

NOT_ENOUGH_MONEY_DICT = {'status': 1, 'error': 'Недостаточно монет', 'type': 1}


def clear_empty_duels():
    ActiveDuel.objects.filter(
        creator__isnull=True,
        opponent__isnull=True,
    ).delete()


def may_be_add_automatic_duel():
    queryset = ActiveDuel.objects.filter(status=ACTIVE_GAME_STATUS.WAITING_FOR_THE_START, is_automatic=True)
    current_amount = len(queryset)

    usernames = []
    for duel in queryset:
        usernames.append(duel.creator.user.username)
        if random() < 0.06:
            delete_waiting_duels_by_user(duel.creator.user)
            # delete_duel_by_id(duel.creator.user, duel.id)

    if random() < (1.0 - 1.0 / (2 + current_amount)):
        return

    for _ in range(5):
        username = f"test{randint(1, BOT_ACCOUNT_AMOUNT)}@mindon.space"
        if username not in usernames:
            user = User.objects.get(username=username)
            delete_waiting_duels_by_user(user)
            create_duel(
                user,
                questions_category=choice(QUESTIONS_CATEGORY_ARRAY),
                duration=choice([30, 60, 120]),
                bet=choice([100, 500, 2000, 10000]),
                is_automatic=True,
            )
            return


def get_duels_waiting_for_the_start(user):
    may_be_add_automatic_duel()
    clear_empty_duels()
    queryset = ActiveDuel.objects.filter(status=ACTIVE_GAME_STATUS.WAITING_FOR_THE_START)
    duels = []
    for duel in queryset:
        duels.append({
            'id': duel.id,
            'isCreator': duel.creator.user == user,
            'creatorRating': duel.creator.user.rating_stars,
            'creatorName': get_user_rating_name(duel.creator.user),
            'bet': duel.bet,
            'duration': duel.duration,
            'questionsCategory': duel.questions_category,
        })

    return duels


def check_duels_are_accessible():
    current_status = DuelsConfiguration.objects.first().status
    if current_status:
        return True
    queryset = ActiveDuel.objects.filter(status=ACTIVE_GAME_STATUS.WAITING_FOR_THE_START)
    for duel in queryset:
        duel.creator.user.coins += duel.bet
        duel.creator.user.save()
        duel.creator.delete()
        duel.delete()
    return False


def get_questions_set(category, amount):
    queryset = TrainerBlock.objects.annotate(question_len=Length('question')).filter(
        question_len__lte=120, active=1, question_type='one')
    if category != QUESTIONS_CATEGORY.ALL:
        categories_names = ["", "", "anc", "ren", "mod"]
        queryset = queryset.filter(section=categories_names[category])
    total_len = len(queryset)
    # print("LEN:", total_len)
    block_amount = total_len // amount
    indexes = []
    for i in range(amount):
        indexes.append(choice(list(range(i * block_amount, (i + 1) * block_amount))))
    # print(indexes)
    # indexes = choices(list(range(total_len)))  # NOOOO 90 60 90 - is bad
    answer = []
    counter = 0
    current = indexes[counter]
    for i, question in enumerate(queryset):
        if i == current:
            # if counter == 0:
            # print("QUESTION #1:", question)
            answer.append(question)
            counter += 1
            if counter >= amount:
                break
            current = indexes[counter]
    shuffle(answer)
    return answer


def create_duel(user, questions_category=QUESTIONS_CATEGORY.ALL, duration=60, bet=100, is_automatic=False):
    if questions_category not in QUESTIONS_CATEGORY_ARRAY or \
            duration not in [30, 60, 120] or bet not in [100, 500, 2000, 10000]:
        return {'status': 1, 'error': 'Запрос не соответствует требованиям', 'type': 0}
    if user.coins < bet:
        return NOT_ENOUGH_MONEY_DICT
    user.coins -= bet
    user.save()
    creator = DuelUserState.objects.create(
        user=user
    )
    # print("CREATOR:", creator)
    new_duel = ActiveDuel.objects.create(
        creator=creator,
        questions_category=questions_category,
        bet=bet,
        duration=duration,
        is_automatic=is_automatic,
    )
    # Сомнительно, ибо, возможно, надо создавать напрямую через таблицу отношений, а оттуда брать queryset,
    # либо вообще ничего не брать, а просто класть нужное в таблицу отношений
    new_duel.trainer_blocks.set(get_questions_set(questions_category, duration))
    new_duel.save()

    return {'status': 0, 'duel': new_duel}


def delete_duel_by_id(user, duel_id):
    try:
        duel = ActiveDuel.objects.get(creator__user=user, id=duel_id)
        user.coins += duel.bet
        creator = duel.creator
        duel.delete()
        creator.delete()
        user.save()
    except:
        pass


def delete_waiting_duels_by_user(user):
    queryset = ActiveDuel.objects.filter(status=ACTIVE_GAME_STATUS.WAITING_FOR_THE_START, creator__user=user)
    # print("TO_DEL_SET:", len(queryset))
    coins = 0
    for duel in queryset:
        duel.creator.delete()
        coins += duel.bet
        duel.delete()
    # queryset.delete()
    user.coins += coins
    user.save()


def accept_duel(user, duel_id, is_automatic=False):
    if is_automatic:
        delete_waiting_duels_by_user(user)
    queryset = ActiveDuel.objects.filter(id=duel_id, status=ACTIVE_GAME_STATUS.WAITING_FOR_THE_START)
    if queryset.exists():
        if (not is_automatic) and queryset.first().bet > user.coins:
            return NOT_ENOUGH_MONEY_DICT
    timestamp_start = datetime.datetime.utcnow() + datetime.timedelta(seconds=12)
    # print("T_START:", timestamp_start)
    opponent = DuelUserState.objects.create(user=user)
    ActiveDuel.objects.filter(id=duel_id, status=ACTIVE_GAME_STATUS.WAITING_FOR_THE_START).update(
        status=ACTIVE_GAME_STATUS.PREPARING, opponent=opponent, timestamp_start=timestamp_start)

    queryset = ActiveDuel.objects.filter(id=duel_id, opponent=opponent)
    if queryset.exists():
        duel = queryset.first()
        if not is_automatic:
            user.coins -= duel.bet
            user.save()
        else:
            duel.is_automatic = 1
            duel.save()
        return {'status': 0, 'duel': duel}
    return {'status': 1}


def may_be_accept_duel_automatic(user):
    queryset = ActiveDuel.objects.filter(creator__user=user, status=ACTIVE_GAME_STATUS.WAITING_FOR_THE_START)
    if queryset.exists():
        now_time = datetime.datetime.utcnow()
        for duel in queryset:
            create_ts = duel.timestamp_create.timestamp()
            seconds_after_create = (now_time - datetime.datetime.utcfromtimestamp(create_ts)).total_seconds()
            if seconds_after_create > BORDER_SECONDS_AMOUNT_TO_AUTOMATIC and random() >= 0.75:
                # username = lambda x: f"test{x}@mindon.space"
                user_bot = User.objects.get(username=f"test{randint(1, BOT_ACCOUNT_AMOUNT)}@mindon.space")
                return accept_duel(user_bot, duel.id, is_automatic=True)

    return {'status': 1}


def get_active_duel(user):
    queryset = ActiveDuel.objects.filter(creator__user=user).exclude(status=ACTIVE_GAME_STATUS.WAITING_FOR_THE_START)
    if queryset.exists():
        # check, that this duel is really active and does not watched by user
        for duel in queryset:
            if duel.creator.question_index < duel.duration:
                return {'status': 0, 'duel': duel}

    queryset = ActiveDuel.objects.filter(opponent__user=user).exclude(status=ACTIVE_GAME_STATUS.WAITING_FOR_THE_START)
    if queryset.exists():
        # check, that this duel is really active and does not watched by user
        for duel in queryset:
            if duel.opponent.question_index < duel.duration:
                return {'status': 0, 'duel': duel}

    return may_be_accept_duel_automatic(user)


def get_questions_dict_array(questions):
    return list(map(lambda x: TrainerBlockSerializer(x).data, questions))


def get_duel_info(duel, user):
    creator_user = duel.creator.user
    opponent_user = duel.opponent.user
    if user not in [creator_user, opponent_user]:
        raise ValueError("Нет прав на просмотр")
    me_is_opponent = user == opponent_user
    opponent = creator_user if me_is_opponent else opponent_user
    my_state = duel.opponent if me_is_opponent else duel.creator

    return {
        'id': duel.id,
        'opponent': get_user_rating_name(opponent),
        'opponentRating': opponent.rating_stars,
        'bet': duel.bet,
        'duration': duel.duration,
        'questionsCategory': duel.questions_category,
        'secondsToStart': int((datetime.datetime.utcfromtimestamp(duel.timestamp_start.timestamp()) -
                               datetime.datetime.utcnow()).total_seconds()),
        'status': duel.status,
        'questions': get_questions_dict_array(duel.trainer_blocks.all()[my_state.question_index:]),
    }


def get_preparing_duel_info(duel, user):
    creator_user = duel.creator.user
    opponent_user = duel.opponent.user
    if user not in [creator_user, opponent_user]:
        raise ValueError("Нет прав на просмотр")
    me_is_opponent = user == opponent_user
    opponent = creator_user if me_is_opponent else opponent_user
    my_state = duel.opponent if me_is_opponent else duel.creator

    return {
        'id': duel.id,
        'opponent': get_user_rating_name(opponent),
        'opponentRating': opponent.rating_stars,
        'bet': duel.bet,
        'duration': duel.duration,
        # 'questionsCategory': duel.questions_category,
        'secondsToStart': int((datetime.datetime.utcfromtimestamp(duel.timestamp_start.timestamp()) -
                               datetime.datetime.utcnow()).total_seconds()),
        'status': duel.status,
        # 'questions': get_questions_dict_array(duel.trainer_blocks.all()[my_state.question_index:]),
    }


def do_automatic_steps(duel: ActiveDuel, is_automatic_opponent=True):
    state = duel.opponent if is_automatic_opponent else duel.creator
    start_ts = duel.timestamp_start.timestamp()
    seconds_from_start = (datetime.datetime.utcnow() - datetime.datetime.utcfromtimestamp(start_ts)).total_seconds()
    need_answers_amount = int(seconds_from_start // AUTOMATIC_SECONDS_TO_ONE_ANSWER)
    have_answers_amount = state.question_index
    if have_answers_amount >= duel.duration or have_answers_amount >= need_answers_amount:
        return
    need_add_answers = int(need_answers_amount - have_answers_amount)
    rating = state.user.rating_stars
    if rating >= 800.0:
        border = 800.0 / rating * 0.34
    else:
        border = 1.0 - rating / 800.0 * 0.65
    for i in range(need_add_answers):
        point = 1 if random() >= border else -1
        state.points = max(0, state.points + point)
    state.question_index = need_answers_amount
    state.save()


def get_active_duel_dict(duel, user):
    creator_state = duel.creator
    opponent_state = duel.opponent
    if user not in [creator_state.user, opponent_state.user]:
        raise ValueError("Нет прав на просмотр")
    me_is_opponent = user == opponent_state.user
    if duel.is_automatic:
        do_automatic_steps(duel, is_automatic_opponent=not me_is_opponent)
    opponent_points = creator_state.points if me_is_opponent else opponent_state.points
    my_points = creator_state.points if not me_is_opponent else opponent_state.points
    return {
        'id': duel.id,
        'secondsLeft': int((datetime.datetime.utcfromtimestamp(duel.timestamp_start.timestamp())
                            + datetime.timedelta(seconds=duel.duration) -
                            datetime.datetime.utcnow()).total_seconds()),
        'status': duel.status,
        'opponentPoints': opponent_points,
        'myPoints': my_points,
    }


def get_completed_duel_dict(duel, user):
    creator_state = duel.creator
    opponent_state = duel.opponent
    if user not in [creator_state.user, opponent_state.user]:
        raise ValueError("Нет прав на просмотр")
    me_is_opponent = user == opponent_state.user
    opponent_points = creator_state.points if me_is_opponent else opponent_state.points
    my_points = creator_state.points if not me_is_opponent else opponent_state.points
    change_opponent_rating = creator_state.rating_changes if me_is_opponent else opponent_state.rating_changes
    change_my_rating = creator_state.rating_changes if not me_is_opponent else opponent_state.rating_changes
    opponent_rating = creator_state.user.rating_stars if me_is_opponent else opponent_state.user.rating_stars
    my_rating = creator_state.user.rating_stars if not me_is_opponent else opponent_state.user.rating_stars
    add_money = 0
    if my_points > opponent_points:
        add_money = int((1 + PROFIT_COEFFICIENT) * duel.bet)
    elif my_points == opponent_points:
        add_money = duel.bet
    return {
        'id': duel.id,
        'status': duel.status,
        'opponentPoints': opponent_points,
        'myPoints': my_points,
        'addMoney': add_money,
        'tax': CHARGE,
        'myRatingChanges': change_my_rating,
        'opponentRatingChanges': change_opponent_rating,
        'myRating': my_rating,
        'opponentRating': opponent_rating,
    }


def get_stars_change(stars_1, stars_2, points_1, points_2, bet):
    bet_coefficient = 1
    if 100 < bet <= 500:
        bet_coefficient = 2
    elif 500 < bet <= 2000:
        bet_coefficient = 3
    elif 2000 < bet:
        bet_coefficient = 4

    stars_difference = abs(stars_1 - stars_2)
    change_1 = 0
    change_2 = 0

    if points_1 == points_2:
        changing = round(stars_difference / 100, 1) * bet_coefficient
        if stars_1 > stars_2:
            change_1 = -min(changing, stars_1)
            change_2 = changing
        elif stars_2 > stars_1:
            change_1 = changing
            change_2 = -min(changing, stars_2)

    elif points_1 > points_2:
        if stars_1 >= stars_2:
            changing = round(200 / (stars_difference + 100), 1) * bet_coefficient
        else:
            changing = round(2 + (stars_difference / 100), 1) * bet_coefficient
        change_1 = changing
        change_2 = -min(changing, stars_2)

    else:
        if stars_1 <= stars_2:
            changing = round(200 / (stars_difference + 100), 1) * bet_coefficient
        else:
            changing = round(2 + (stars_difference / 100), 1) * bet_coefficient
        change_1 = -min(changing, stars_1)
        change_2 = changing
    return [change_1, change_2]


def create_completed_duel(duel: ActiveDuel):
    CompletedDuel.objects.create(
        creator=duel.creator,
        opponent=duel.opponent,
        timestamp_create=duel.timestamp_create,
        is_automatic=duel.is_automatic,

        duration=duel.duration,
        bet=duel.bet,
        questions_category=duel.questions_category,
    )


def save_duel_results(duel):
    creator_state = duel.creator
    opponent_state = duel.opponent

    if opponent_state.points == creator_state.points:
        opponent_state.user.coins += duel.bet
        creator_state.user.coins += duel.bet
    elif opponent_state.points > creator_state.points:
        opponent_state.user.coins += int((1 + PROFIT_COEFFICIENT) * duel.bet)
    else:
        creator_state.user.coins += int((1 + PROFIT_COEFFICIENT) * duel.bet)

    stars_change_creator, stars_change_opponent = get_stars_change(
        creator_state.user.rating_stars,
        opponent_state.user.rating_stars,
        creator_state.points,
        opponent_state.points,
        duel.bet
    )
    creator_state.rating_changes = stars_change_creator
    opponent_state.rating_changes = stars_change_opponent

    creator_state.user.rating_stars += stars_change_creator
    opponent_state.user.rating_stars += stars_change_opponent

    creator_state.user.save()
    opponent_state.user.save()
    creator_state.save()
    opponent_state.save()


def automatic_save_results_and_delete_very_old_duel(duel: ActiveDuel):
    creator_state = duel.creator
    opponent_state = duel.opponent
    if creator_state.question_index != duel.duration + 1 and opponent_state.question_index != duel.duration + 1:
        save_duel_results(duel)
    create_completed_duel(duel)
    duel.delete()


def clear_old_duels():
    active_duels = ActiveDuel.objects.all()
    for duel in active_duels:
        try:
            start_time = duel.timestamp_start
            if start_time:
                start_ts = start_time.timestamp()
                seconds_from_start = (datetime.datetime.utcnow() -
                                      datetime.datetime.utcfromtimestamp(start_ts)).total_seconds()
                if seconds_from_start > 60 * 60 * 24:  # 1 day
                    automatic_save_results_and_delete_very_old_duel(duel)
        except Exception as e:
            print("Error during delete old duel:", e)


def get_active_duel_info_by_id(duel_id, user):
    duel = ActiveDuel.objects.get(id=duel_id)
    creator_state = duel.creator
    opponent_state = duel.opponent
    if user not in [creator_state.user, opponent_state.user]:
        raise ValueError("Нет прав на просмотр")

    now_time = datetime.datetime.utcnow()
    # now_time_ts = now_time.timestamp()
    start_ts = duel.timestamp_start.timestamp()
    seconds_to_start = (datetime.datetime.utcfromtimestamp(start_ts) - now_time).total_seconds()
    if seconds_to_start > 0:
        # print("NOW Is smaller then start")
        return get_preparing_duel_info(duel, user)
    if duel.status == ACTIVE_GAME_STATUS.PREPARING:
        duel.status = ACTIVE_GAME_STATUS.IN_PROGRESS
        duel.save()

    # time_end = duel.timestamp_start + datetime.timedelta(seconds=duel.duration)
    # time_end_ts = time_end.timestamp()
    seconds_to_end = (datetime.datetime.utcfromtimestamp(start_ts)
                      + datetime.timedelta(seconds=duel.duration) -
                      now_time).total_seconds()
    if seconds_to_end < 0:
        duel = ActiveDuel.objects.get(id=duel_id)
        if duel.status in [ACTIVE_GAME_STATUS.TIME_OUT, ACTIVE_GAME_STATUS.COMPLETED]:
            while duel.status == ACTIVE_GAME_STATUS.TIME_OUT:
                duel = ActiveDuel.objects.get(id=duel_id)
                sleep(0.1)

            me_is_opponent = user == opponent_state.user
            my_state = opponent_state if me_is_opponent else creator_state

            duel_dict = get_completed_duel_dict(duel, user)

            if my_state.question_index < duel.duration + 1:
                create_completed_duel(duel)
                duel.delete()

            return duel_dict

        else:
            duel.status = ACTIVE_GAME_STATUS.TIME_OUT
            duel.save()

            save_duel_results(duel)

            if user == duel.opponent.user: # me is opponent
                duel.opponent.question_index = duel.duration + 1
                duel.opponent.save()
            else:
                duel.creator.question_index = duel.duration + 1
                duel.creator.save()

            # me_is_opponent = user == duel.opponent_state.user
            # my_state = duel.opponent_state if me_is_opponent else duel.creator_state
            # my_state.question_index = duel.duration + 1
            #
            # creator_state.user.save()
            # opponent_state.user.save()
            # creator_state.save()
            # opponent_state.save()

            duel.status = ACTIVE_GAME_STATUS.COMPLETED
            duel.save()

            duel_dict = get_completed_duel_dict(duel, user)

            if duel.is_automatic:
                create_completed_duel(duel)
                duel.delete()

            return duel_dict

    return get_active_duel_dict(duel, user)


def add_user_answer(user, duel_id, question_id, answer):
    duel = ActiveDuel.objects.get(id=duel_id)
    creator_state = duel.creator
    opponent_state = duel.opponent
    if user not in [creator_state.user, opponent_state.user]:
        raise ValueError("Нет прав на просмотр")

    # print("ALL:", duel.trainer_blocks.filter(id=11))
    # print("QUESTION ID:", question_id)

    now_time = datetime.datetime.utcnow()
    start_ts = duel.timestamp_start.timestamp()
    seconds_to_end = (datetime.datetime.utcfromtimestamp(start_ts)
                      + datetime.timedelta(seconds=duel.duration) -
                      now_time).total_seconds()
    if seconds_to_end < 0:
        return get_active_duel_info_by_id(duel_id, user)

    me_is_opponent = user == opponent_state.user
    my_state = opponent_state if me_is_opponent else creator_state

    # print("ALL:", duel.trainer_blocks.all())

    questions = duel.trainer_blocks.filter(id=question_id)
    # questions = duel.trainer_blocks.all()[my_state.question_index:] #filter(id=question_id).first()
    # print("MY INDEX:", my_state.question_index)
    # for i, question in enumerate(questions):
    #     if question.id != question_id:
    #         continue
    if questions.exists():
        question = questions.first()
        valid_answers = json.loads(question.valid_answers)
        is_valid = answer in valid_answers
        if is_valid:
            my_state.points += 1
        elif my_state.points > 0:
            my_state.points -= 1
        my_state.question_index += 1
        my_state.save()

        if question.question_type != QUESTION_TYPES.REASONS_AND_ARGUMENTS:
            TrainerBlockLog.objects.create(
                user=user,
                trainer_block=question,
                is_valid=is_valid,
                answer=str(answer)[:100]
            )
        trainer_block_progress, _ = TrainerBlockProgress.objects.get_or_create(
            trainer_block=question,
            user=user)
        trainer_block_progress.attempts += 1
        trainer_block_progress.successful_attempts += 1 if is_valid else 0
        trainer_block_progress.save()

    return get_active_duel_dict(duel, user)
