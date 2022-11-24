from datetime import datetime
import json
import math
from django.db.models import Sum
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response

from APIBackendService.views import AppAPIView
from Content.models import TrainerBlockTag, TrainerBlockPeriod
from Statistics.models import ActivityLog
from Statistics.serializers import ActivityLogPostSerializer
from Statistics.serializers import TrainerBlockProgress
from Content.utils.products import get_active_trainer_blocks
from Statistics.service import create_activity_log, add_ratings_requests_amount
from .metrics import totals


class SectionProgressView(AppAPIView):
    """
    Summary statistics view for main sections of content
    """

    @swagger_auto_schema(
        operation_summary='Get summary statistics',
        operation_description='Get summary statistics',
        manual_parameters=[
            openapi.Parameter('section', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False,
                              description="Section"),
        ],
        responses={
            200: 'OK',
            400: 'Bad request',
        }
    )
    def get(self, request):
        trainer_blocks = get_active_trainer_blocks()
        if 'section' in request.query_params.keys():
            trainer_blocks = trainer_blocks.filter(section=request.query_params['section'])
            tags = TrainerBlockTag.objects.all()
            result = {}
            for tag in tags:
                trainer_blocks_with_tag = tag.trainer_blocks.all() \
                    .intersection(trainer_blocks).values_list('id', flat=True)
                trainer_progress_with_tag = TrainerBlockProgress.objects.filter(
                    user=request.user,
                    trainer_block__in=trainer_blocks_with_tag,
                    successful_attempts__gt=0
                )
                ratio = trainer_progress_with_tag.count() / trainer_blocks_with_tag.count()
                score = int(math.sin((math.pi / 2) * ratio) * 100)
                result[tag.tag] = score
        else:
            result = {}
            for section in ['anc', 'ren', 'mod']:
                section_trainer_blocks = trainer_blocks.filter(section=section)
                trainer_progress = TrainerBlockProgress.objects.filter(
                    user=request.user,
                    trainer_block__in=section_trainer_blocks,
                    successful_attempts__gt=0
                )
                ratio = trainer_progress.count() / section_trainer_blocks.count()
                result[section] = int(math.sin((math.pi / 2) * ratio) * 100)
        return Response(result)


class StatisticProgressView(AppAPIView):
    """
    Statistics progress for selected chapter
    """

    @swagger_auto_schema(
        operation_summary='Get statistics',
        operation_description='Get statistics for selected chapter',
        manual_parameters=[
            openapi.Parameter('section', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False,
                              description="Section"),
            openapi.Parameter('period', in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=False,),
            openapi.Parameter('person', in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=False,),
            openapi.Parameter('type', in_=openapi.IN_QUERY, description="common/detail",
                              type=openapi.TYPE_STRING, required=False,),
        ],
        responses={
            200: 'OK',
            400: 'Bad request',
        }
    )
    def get(self, request):
        request_section = request.query_params.get('section', '')
        request_period = request.query_params.get('period', '')
        request_person = request.query_params.get('person', '')
        request_type = request.query_params.get('type', 'common')
        user = request.user

        create_activity_log(user, f"STAT {request_section},{request_period},{request_person},{request_type[0]}")

        trainer_blocks = get_active_trainer_blocks()
        is_anc_period = False
        if request_person:
            blocks = trainer_blocks.filter(persons__person__in=[request_person])
            trainer_total = TrainerBlockProgress.objects.filter(
                user=user,
                trainer_block__in=blocks,
            )
        elif request_period:
            blocks = trainer_blocks.filter(periods__period__in=[request_period])
            # print("Len", len(blocks))
            trainer_total = TrainerBlockProgress.objects.filter(
                user=user, trainer_block__in=blocks,
            )
            t = TrainerBlockPeriod.objects.filter(period=request_period, section='anc')
            if t.exists():
                is_anc_period = True
        elif request_section:
            blocks = trainer_blocks.filter(section=request_section)
            trainer_total = TrainerBlockProgress.objects.filter(
                user=user, trainer_block__in=blocks,
            )
        else:
            trainer_total = TrainerBlockProgress.objects.filter(
                user=user
            )
            blocks = trainer_blocks.all()

        total_attempts = trainer_total.aggregate(Sum('attempts'))['attempts__sum']
        total_right = trainer_total.aggregate(Sum('successful_attempts'))['successful_attempts__sum']

        answer = dict()
        amount = blocks.count()
        right = trainer_total.filter(successful_attempts__gt=0).count()
        answer['amount'] = amount
        answer['right'] = right if right else 0
        answer['total_attempts'] = total_attempts if total_attempts else 0
        answer['total_right'] = total_right if total_right else 0
        try:
            progress = right / amount
        except:
            progress = 0
        answer['linear_progress'] = int(progress * 100)  # покрыто вопросов
        answer['progress'] = int(math.sin((math.pi / 2) * progress) * 100)  # усвоено информации

        if not (request_section or request_period or request_person) and request_type == 'common':
            sections = {
                'anc': {'name': 'Древность и средневековье', 'value': 'anc', 'r': 0, 't': 0.000001, 'p': 0},
                'ren': {'name': 'Новое время', 'value': 'ren', 'r': 0, 't': 0.000001, 'p': 0},
                'mod': {'name': 'Новейшее время', 'value': 'mod', 'r': 0, 't': 0.000001, 'p': 0},
            }
            for section in sections.keys():
                section_trainer_blocks = trainer_blocks.filter(section=section)
                trainer_progress = TrainerBlockProgress.objects.filter(
                    user__exact=request.user,
                    trainer_block__in=section_trainer_blocks,
                    successful_attempts__gt=0
                )
                try:
                    progress = trainer_progress.count() / section_trainer_blocks.count()
                    sections[section]['p'] = int(math.sin((math.pi / 2) * progress) * 100)
                except:
                    pass
            answer['type'] = 'common'
            answer['next_type'] = 'section'
            answer['data'] = [{
                'name': s['name'],
                'section': s['value'],
                'description': '',
                # 'right': s['r'],
                'progress': s['p']
            } for s in sections.values()]
        elif request_section and request_type == 'common':
            periods = TrainerBlockPeriod.objects.filter(section=request_section)
            periods_array = []
            for period in periods:
                period_trainer_blocks = trainer_blocks.filter(periods__period__in=[period.period])
                trainer_progress = TrainerBlockProgress.objects.filter(
                    user=user,
                    trainer_block__in=period_trainer_blocks,
                    successful_attempts__gt=0
                )
                try:
                    progress = trainer_progress.count() / period_trainer_blocks.count()
                    periods_array.append({
                        'name': period.name,
                        'description': period.description,
                        'period': period.period,
                        'progress': int(math.sin((math.pi / 2) * progress) * 100),
                    })
                except:
                    pass
            answer['type'] = 'common'
            answer['next_type'] = 'period'
            answer['data'] = periods_array
        elif request_period and request_type == 'common' and not is_anc_period:
            persons = TrainerBlockPeriod.objects.filter(period=request_period)[0].persons.all()
            persons_array = []
            # print("9", persons, type(persons), type(persons.persons))
            for person in persons:
                person_trainer_blocks = trainer_blocks.filter(persons__person__in=[person.person])
                trainer_progress = TrainerBlockProgress.objects.filter(
                    user=user,
                    trainer_block__in=person_trainer_blocks,
                    successful_attempts__gt=0
                )
                try:
                    progress = trainer_progress.count() / person_trainer_blocks.count()
                    persons_array.append({
                        'name': person.name,
                        'description': person.description,
                        'person': person.person,
                        'progress': int(math.sin((math.pi / 2) * progress) * 100),
                    })
                except:
                    pass
            answer['type'] = 'common'
            answer['next_type'] = 'person'
            answer['data'] = persons_array

        elif request_person or is_anc_period or request_type == 'detail':

            sorted_progress = sorted(trainer_total, key=lambda x: -x.attempts + x.successful_attempts)

            tags = TrainerBlockTag.objects.all()
            tags_res = []
            for tag in tags:
                trainer_blocks_with_tag = tag.trainer_blocks.all() \
                    .intersection(blocks).values_list('id', flat=True)
                # print("8")
                trainer_progress_with_tag = TrainerBlockProgress.objects.filter(
                    user=user,
                    trainer_block__in=trainer_blocks_with_tag,
                    successful_attempts__gt=0
                )
                try:
                    ratio = trainer_progress_with_tag.count() / trainer_blocks_with_tag.count()
                    score = int(math.sin((math.pi / 2) * ratio) * 100)
                    # result[tag.tag] = score
                    tags_res.append({'tag': tag.tag, 'name': tag.description, 'score': score})
                except:
                    pass

            answer['type'] = 'detail'
            answer['tags'] = tags_res
            answer['difficult'] = [{
                'question': item.trainer_block.question,
                'valid_answers': item.trainer_block.valid_answers,
                'answers': item.trainer_block.answers,
                'attempts': item.attempts,
                'successful_attempts': item.successful_attempts
            } for item in sorted_progress[0:10]]

        return Response(answer)


class EventView(AppAPIView):
    """
    Save event about any activity in app
    """

    @swagger_auto_schema(
        operation_summary='Save activity',
        operation_description='Save activity',
        request_body=ActivityLogPostSerializer,
        responses={
            200: 'OK',
            400: 'Bad request',
        }
    )
    def post(self, request):
        serializer = ActivityLogPostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        ActivityLog.objects.create(
            user=request.user,
            activity=data['activity'],
            payload=json.dumps(data['meta']),
            timestamp=datetime.now(),
        )
        return Response('OK')


# http://localhost:8000/api/statistics/rating/
class WeekRatingView(AppAPIView):
    """
    Current week rating status
    """

    @swagger_auto_schema(
        operation_summary='Week rating',
        operation_description='Get week rating',
        responses={
            200: 'OK',
            400: 'Bad request',
        }
    )
    def get(self, request):
        metric_action = request.GET.get('action', 'get')
        metric_top = min(int(request.GET.get('top', 70)), 100)
        ans = []
        if metric_action == 'get':
            try:
                add_ratings_requests_amount()
            except:
                pass
            ans = totals.get_rating(top_n=metric_top)
        prev = totals.get_previous_week_leaders()
        user_info = totals.get_user_rating_info(request.user)

        return Response({"data": ans,
                         "previous": prev,
                         "user": user_info,
                         "day": totals.get_expired_week_time()})
