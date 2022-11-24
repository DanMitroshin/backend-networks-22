import re
import datetime
import json

from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework.views import APIView
from rest_framework.exceptions import ParseError
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework import status

from APIBackendService.views import AppAPIView
from Content.serializers.product import LessonGetSerializer, ProductPreOpenSerializer, ContentThemeMainInfoSerializer, \
    ProductLogCreateSerializer
from Content.utils.special_questions import save_special_answers
from Content.utils import (
    validate_access,
)
from Content.utils.products import generate_product, update_product_progress, update_coins_for_product

from Content.constants import (
    LESSONS,
    LESSON_TYPES,
    GENERATED_PRODUCT_TYPES,
)

from Content.models import (
    Product,
    TrainerBlock,
    ContentTheme,
)
from Content.serializers import (
    MediaProductSerializer,
    MediaProductPostSerializer,
    TrainerBlockSerializer,
    TrainerProductCreateRetrieveSerializer,
    TrainerProductPostSerializer,
    TrainerBlocksPostSerializer,
    TrainerProductSerializer,
    ProductListGetSerializer,
    UserAnswerForReviewCreateSerializer, TrainerBlockCheckAnswerSerializer)
from Services.service import alert_admin_message

from Statistics.metrics.totals import update_rating
from Statistics.utils import update_product_achievements
from Statistics.service import add_answers_to_app_metrics

from Content.constants import QUESTION_TYPES
from Statistics.utils.user_metrics import get_user_success_answers_amount, update_user_read_theory_blocks_amount, \
    get_user_read_theory_blocks_amount
from Users.utils import get_ban_info_about_user


# http://localhost:8000/api/history/content/lessons/list/
from Users.utils.permissions import check_has_content_access


class LessonListView(AppAPIView):
    """
    Lessons list view.
    """

    @swagger_auto_schema(
        operation_summary='Lessons list',
        operation_description='Lessons list',
        query_serializer=ProductListGetSerializer(),
        responses={
            200: 'OK',
            400: 'Bad request',
            403: 'Not permitted',
        }
    )
    def get(self, request):

        # version = int(request.query_params.get('version', 1)) CURRENT: 3

        serializer = ProductListGetSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        products_queryset = Product.objects.all()
        if 'section' in serializer.validated_data:
            products_queryset = products_queryset.filter(section__exact=serializer.validated_data['section'])
        if 'lesson_type' in serializer.validated_data:
            products_queryset = products_queryset.filter(lesson_type__exact=serializer.validated_data['lesson_type'])

        if serializer.validated_data['lesson_type'] == LESSON_TYPES.P1_INFORMATIONAL_LESSON:
            result = {
                LESSONS: [],
            }

            products_queryset = products_queryset.filter(active=2).order_by('index')
            for product in products_queryset:

                lesson_dict = ProductPreOpenSerializer(product, context={'user': request.user}).data

                if product.content_theme:
                    lesson_dict['theme'] = {
                        "name": product.content_theme.name,
                        "index": product.content_theme.index
                    }
                    if product.content_theme.video:
                        lesson_dict["videoId"] = product.content_theme.video.index

                result[LESSONS].append(lesson_dict)

            return Response(result)

        if serializer.validated_data['lesson_type'] == LESSON_TYPES.P2_HANDCRAFTED_TRAINER_LESSON:  # and request.user.is_staff:
            products_queryset = products_queryset.filter(active__in=[1, 2], content_theme__index__gt=0)

            result = {
                LESSONS: [],
            }

            for theme in products_queryset.values_list('content_theme', flat=True).distinct():
                content_theme = ContentTheme.objects.get(id=theme)

                theme_dict = ContentThemeMainInfoSerializer(
                    content_theme, context={
                        'user': request.user,
                        "products_filter": {
                            "active__in": [1, 2],
                            "section__exact": serializer.validated_data['section'],
                            "lesson_type__exact": serializer.validated_data['lesson_type'],
                        }
                    }
                ).data

                result[LESSONS].append(theme_dict)

            result[LESSONS] = sorted(result[LESSONS], key=lambda a: a['index'])

            return Response(result)


# CHANGES:
# - in content theme:
#   - REMOVE key
#   - lesson_name -> name
#   - type -> lesson_type
class LessonView(AppAPIView):
    """
    Lesson get and save results/answers.
    """

    @swagger_auto_schema(
        operation_summary='Lesson get',
        operation_description='Lesson get (test or theory)',
        query_serializer=LessonGetSerializer(),
        responses={
            200: 'OK',
            400: 'Bad request',
            403: 'Not permitted',
        }
    )
    def get(self, request):

        user = request.user
        params_serializer = LessonGetSerializer(data=request.query_params)
        params_serializer.is_valid(raise_exception=True)
        params = params_serializer.save()

        product = get_object_or_404(Product, pk=params.lesson)
        validate_access(user, product)

        if params.lesson_type == LESSON_TYPES.P1_INFORMATIONAL_LESSON:
            result = MediaProductSerializer(product).data
            total_read_theory_blocks = get_user_read_theory_blocks_amount(user)

        else:  # [LESSON_TYPES.P2_HANDCRAFTED_TRAINER_LESSON, ]

            # [DEPRECATED: MOVED TO /trainers]
            # else:  # params.lesson_type == LESSON_TYPES.P3_AUTOGENERATED_TRAINER_LESSON
            #     product = generate_product(user, product_type=GENERATED_PRODUCT_TYPES.PERSONAL)
            result = TrainerProductSerializer(product, context={
                'user': user,
                'has_content_access': check_has_content_access(user),
            }).data

        try:
            if product.content_theme:
                theme_dict = ContentThemeMainInfoSerializer(product.content_theme, context={'user': user}).data
                theme_dict['lessons'] = list(filter(lambda x: x['id'] != product.id, theme_dict['lessons']))

                if "videoId" in theme_dict.keys():
                    result["videoId"] = theme_dict["videoId"]

                result["content_theme"] = theme_dict
        except:
            pass
        return Response(result)

    @swagger_auto_schema(
        operation_summary='Save lesson progress',
        operation_description='Save lesson progress',
        responses={
            200: 'OK',
            400: 'Bad request',
            403: 'Not permitted',
        }
    )
    def post(self, request):

        # try:

        lesson_id = int(request.data.get('lesson_id', -1))
        is_product_related = True if lesson_id >= 0 else False
        user = request.user

        special_answers = request.data.get('special_answers', [])
        save_special_answers(user, special_answers)

        has_ban, ban_info = get_ban_info_about_user(user)

        # Validating
        product = None
        if is_product_related:
            product = get_object_or_404(Product, id=lesson_id)
            request_serializer = (
                MediaProductPostSerializer(data=request.data)
                if product.lesson_type == LESSON_TYPES.P1_INFORMATIONAL_LESSON
                else TrainerProductPostSerializer(data=request.data)
            )

        else:
            request_serializer = TrainerBlocksPostSerializer(data=request.data)

        request_serializer.is_valid(raise_exception=True)
        valid_data = request_serializer.validated_data
        currently_completed, completed = 0, 0
        points = 0
        result = {}

        # Lesson type specific changes
        if is_product_related and product.lesson_type == LESSON_TYPES.P1_INFORMATIONAL_LESSON:
            completed = valid_data['last_block']
            currently_completed = completed

            total_read_theory_blocks = get_user_read_theory_blocks_amount(user)
            update_user_read_theory_blocks_amount(user, currently_completed)

            # NEED TO PROCESS THIS POINT IN APP, I MIXED UP FUNCTIONS
            # if user.username == 'denismitroshin':
            #     result['saleOfferInfo'] = create_sale_offer_after_20_read_blocks(user)
            # if False and total_read_theory_blocks < 20 and total_read_theory_blocks + currently_completed >= 20:
            #     result['saleOfferInfo'] = create_sale_offer_after_20_read_blocks(user)
        else:
            # valid_data['answers'] = [{'id': 3264, 'answer': ['a', 'b']}]

            for answer in valid_data['answers']:
                # try:
                answer_serializer = TrainerBlockCheckAnswerSerializer(data=answer)
                # print("DATA:", answer)
                answer_serializer.is_valid(raise_exception=True)
                answer_result = answer_serializer.save(user=request.user, calculate_points=not has_ban)
                #     print(answer_result)
                # except Exception as e:
                #     print("Err", e)
                #     raise ValueError

                currently_completed += 1 if answer_result.is_valid else 0
                completed += 1 if answer_result.completed else 0
                points += answer_result.points

            # UPDATE APP METRICS
            add_answers_to_app_metrics(
                right_answers=currently_completed,
                total_answers=len(valid_data['answers']),
            )

            # UPDATE USER ACHIEVEMENTS
            total_success_answers = get_user_success_answers_amount(user)
            update_product_achievements(user, currently_completed, product=product)

        # Saving
        product_progress = None
        if is_product_related:
            product_progress = update_product_progress(product, user, completed)
            product_log_serializer = ProductLogCreateSerializer(data={
                'product': product.id,
                'user': user.id,
                'time_to_complete': datetime.timedelta(seconds=valid_data['time']),
                'completed': currently_completed,
            })
            product_log_serializer.is_valid(raise_exception=True)
            product_log_serializer.save()

        # туть p2 и p3
        coins = 0
        if (not is_product_related) or product.lesson_type != LESSON_TYPES.P1_INFORMATIONAL_LESSON:
            coins = update_coins_for_product(user, currently_completed)
            update_rating(request.user, points, has_ban=has_ban)

        result.update({
            'points': points,
            'extra_points': 0,
            'has_ban': has_ban,
            'coins': coins,
            'userCoins': user.coins,
        })
        if has_ban:
            result['limit'] = ban_info['limit']

        if product_progress is not None:
            result['progress'] = product_progress.progress

        # except Exception as e:
        #     print("Err", e)
        return Response(result)


# http://localhost:8000/api/history/content/questions/check/
class QuestionCheckView(AppAPIView):
    """
    Check one question (for arguments type usually)
    """
    @swagger_auto_schema(
        operation_summary='Check answer',
        operation_description='Question check answer',
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True,
                              description="Question id"),
            openapi.Parameter('answer', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True,
                              description="Answer str"),
        ],
        responses={
            200: 'OK',
            400: 'Bad request',
            403: 'Not permitted',
        }
    )
    def post(self, request):

        user = request.user
        data = request.data
        id_question = data["id"]
        user_answer = data["answer"]
        question = get_object_or_404(TrainerBlock, id=id_question)

        if question.question_type == QUESTION_TYPES.REASONS_AND_ARGUMENTS:
            MAX_LENGTH_ANSWER = 180
            if len(user_answer) > MAX_LENGTH_ANSWER:
                alert_admin_message(
                    f"<b>Получен длинный ({len(user_answer)} > {MAX_LENGTH_ANSWER}) ответ на вопрос</b> "
                    f"(id {question.id}):\n{user_answer}")
                raise ParseError(detail=f'Слишком длинный ответ ({len(user_answer)} > {MAX_LENGTH_ANSWER})')

            exclude_array = data.get("exclude_array", [])

            answer_serializer = TrainerBlockCheckAnswerSerializer(
                data={'answer': user_answer, 'id': id_question},
                context={"single_answer": True, 'exclude_ids_array': exclude_array},
            )
            answer_serializer.is_valid(raise_exception=True)
            answer_result = answer_serializer.save(user=user, calculate_points=False)

            check_meta = answer_result.meta_info

            result = {
                'is_valid': answer_result.is_valid,
                'is_copy': check_meta['is_copy'],
                'id_answer': check_meta['trainer_block_log_id'],
            }

            if answer_result.is_valid:
                result['match_phrase'] = check_meta['match_phrase']
                result['id_match'] = check_meta['id_match']
            # except Exception as e:
            #     print("err", e)

            return Response(result)

        return Response(200)


# http://localhost:8000/api/history/content/answers/review/
class AddUserAnswerForReviewView(AppAPIView):
    """
    Review view: add answers that the user considers correct to review
    """

    @swagger_auto_schema(
        operation_summary='Review answer',
        operation_description='Send user answer for review',
        request_body=UserAnswerForReviewCreateSerializer,
        responses={
            200: 'OK',
            400: 'Bad request',
        }
    )
    def post(self, request):
        serializer = UserAnswerForReviewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        return Response(200)


# http://localhost:8000/api/history/content/trainers/
class TrainerProductCreateRetrieveView(AppAPIView):
    """
    Create personal train product
    """

    @swagger_auto_schema(
        operation_summary='Create train',
        operation_description='Create train product',
        query_serializer=TrainerProductCreateRetrieveSerializer(),
        responses={
            200: 'OK',
            400: 'Bad request',
        }
    )
    def get(self, request):
        serializer = TrainerProductCreateRetrieveSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        product = generate_product(request.user, **data)
        result = TrainerProductSerializer(product, context={'user': request.user}).data
        # except Exception as e:
        #     print("ERR", e)
        return Response(result)
