from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication

from APIBackendService.views import AppAPIView
from Games.utils.duels_v1 import get_active_duel, get_duel_info, get_duels_waiting_for_the_start, \
    delete_waiting_duels_by_user, delete_duel_by_id, create_duel, accept_duel, add_user_answer, \
    get_active_duel_info_by_id, check_duels_are_accessible

from Games.constants import DUEL_EVENTS

EVENT = 'event'
PAYLOAD = 'payload'
COINS = 'coins'


class DuelsListView(AppAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Duels list',
        operation_description='Duels list',
        responses={
            200: 'OK',
            400: 'Bad request',
        }
    )
    def get(self, request):
        user = request.user
        active_duel_info = get_active_duel(user)
        if active_duel_info["status"] == 0:
            return Response({
                EVENT: DUEL_EVENTS.IN_DUEL_ROOM,
                PAYLOAD: get_duel_info(active_duel_info['duel'], user),
                COINS: user.coins,
            })

        # access = check_duels_are_accessible()
        if not check_duels_are_accessible():
            return Response({
                EVENT: DUEL_EVENTS.DUELS_ARE_OFF,
                PAYLOAD: {},
                COINS: user.coins,
            })

        return Response({
            EVENT: DUEL_EVENTS.UPDATE_DUEL_LIST,
            PAYLOAD: {
                'list': get_duels_waiting_for_the_start(user),
            },
            COINS: user.coins,
        })


class DeleteDuelView(AppAPIView):
    """
    Delete duel
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Delete duel',
        operation_description='Delete duel',
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True,
                              description="Duel id"),
        ],
        responses={
            200: 'OK',
            400: 'Bad request',
        }
    )
    def get(self, request):
        user = request.user
        duel_id = int(request.query_params['id'])

        active_duel_info = get_active_duel(user)
        if active_duel_info["status"] == 0:
            return Response({
                EVENT: DUEL_EVENTS.IN_DUEL_ROOM,
                PAYLOAD: get_duel_info(active_duel_info['duel'], user),
                COINS: user.coins,
            })

        if not check_duels_are_accessible():
            return Response({
                EVENT: DUEL_EVENTS.DUELS_ARE_OFF,
                PAYLOAD: {},
                COINS: user.coins,
            })

        # delete_waiting_duels_by_user(user)
        delete_duel_by_id(user, duel_id)

        return Response({
            EVENT: DUEL_EVENTS.UPDATE_DUEL_LIST,
            PAYLOAD: {
                'list': get_duels_waiting_for_the_start(user),
            },
            COINS: user.coins,
        })


class CreateDuelView(AppAPIView):
    """
    Create duel
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Create duel',
        operation_description='Create duel',
        manual_parameters=[
            openapi.Parameter('duration', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True,
                              description="Duel duration"),
            openapi.Parameter('bet', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True,
                              description="Duel bet"),
            openapi.Parameter('category', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True,
                              description="Duel category"),
        ],
        responses={
            200: 'OK',
            400: 'Bad request',
        }
    )
    def get(self, request):
        user = request.user

        active_duel_info = get_active_duel(user)
        if active_duel_info["status"] == 0:
            return Response({
                EVENT: DUEL_EVENTS.IN_DUEL_ROOM,
                PAYLOAD: get_duel_info(active_duel_info['duel'], user),
                COINS: user.coins,
            })

        if not check_duels_are_accessible():
            return Response({
                EVENT: DUEL_EVENTS.DUELS_ARE_OFF,
                PAYLOAD: {},
                COINS: user.coins,
            })

        delete_waiting_duels_by_user(user)

        duration = int(request.query_params['duration'])
        bet = int(request.query_params['bet'])
        category = int(request.query_params['category'])

        create_info = create_duel(
            user,
            questions_category=category,
            duration=duration,
            bet=bet
        )

        if create_info['status'] == 1:
            return Response({
                EVENT: DUEL_EVENTS.ERROR,
                PAYLOAD: {
                    'error': create_info['error'],
                    'type': create_info['type'],
                },
                COINS: user.coins,
            })

        return Response({
            EVENT: DUEL_EVENTS.UPDATE_DUEL_LIST,
            PAYLOAD: {
                'list': get_duels_waiting_for_the_start(user),
            },
            COINS: user.coins,
        })


class AcceptDuelView(AppAPIView):
    """
    Accept duel (by id)
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Accept duel',
        operation_description='Accept duel',
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True,
                              description="Duel id to accept"),
        ],
        responses={
            200: 'OK',
            400: 'Bad request',
        }
    )
    def get(self, request):
        user = request.user
        duel_id = int(request.query_params['id'])

        active_duel_info = get_active_duel(user)
        if active_duel_info["status"] == 0:
            return Response({
                EVENT: DUEL_EVENTS.IN_DUEL_ROOM,
                PAYLOAD: get_duel_info(active_duel_info['duel'], user),
                COINS: user.coins,
            })

        if not check_duels_are_accessible():
            return Response({
                EVENT: DUEL_EVENTS.DUELS_ARE_OFF,
                PAYLOAD: {},
                COINS: user.coins,
            })

        delete_waiting_duels_by_user(user)
        accept_result = accept_duel(user, duel_id)
        if accept_result['status'] == 0:
            return Response({
                EVENT: DUEL_EVENTS.IN_DUEL_ROOM,
                PAYLOAD: get_duel_info(accept_result['duel'], user),
                COINS: user.coins,
            })

        elif 'error' in accept_result.keys():
            return Response({
                EVENT: DUEL_EVENTS.ERROR,
                PAYLOAD: {
                    'error': accept_result['error'],
                    'type': accept_result['type'],
                },
                COINS: user.coins,
            })

        return Response({
            EVENT: DUEL_EVENTS.UPDATE_DUEL_LIST,
            PAYLOAD: {
                'list': get_duels_waiting_for_the_start(user),
            },
            COINS: user.coins,
        })


class AnswerDuelView(AppAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Add answer',
        operation_description='Add duel question answer',
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True,
                              description="Duel id"),
            openapi.Parameter('questionId', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True,
                              description="Question id"),
            openapi.Parameter('answer', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True,
                              description="Answer"),
        ],
        responses={
            200: 'OK',
            400: 'Bad request',
        }
    )
    def get(self, request):
        user = request.user
        duel_id = int(request.query_params['id'])
        question_id = int(request.query_params['questionId'])
        answer = request.query_params['answer']

        answer_info = add_user_answer(user, duel_id, question_id, answer)

        return Response({
            EVENT: DUEL_EVENTS.IN_DUEL_ROOM,
            PAYLOAD: answer_info,
            COINS: user.coins,
        })


class UpdateDuelView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Update duel',
        operation_description='Update duel current config',
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True,
                              description="Duel id to update"),
        ],
        responses={
            200: 'OK',
            400: 'Bad request',
        }
    )
    def get(self, request):
        user = request.user
        duel_id = int(request.query_params['id'])

        answer_info = get_active_duel_info_by_id(duel_id, user)

        return Response({
            EVENT: DUEL_EVENTS.IN_DUEL_ROOM,
            PAYLOAD: answer_info,
            COINS: user.coins,
        })


class ExitDuelsRoomView(AppAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Exit duels',
        operation_description='Exit from duels room',
        responses={
            200: 'OK',
        }
    )
    def get(self, request):
        user = request.user

        delete_waiting_duels_by_user(user)

        return Response({
            EVENT: DUEL_EVENTS.UPDATE_DUEL_LIST,
            PAYLOAD: {
                'list': [],
            },
            COINS: user.coins,
        })


class TestDuelView(AppAPIView):
    """
    Test view.
    """

    def get(self, request):
        # clear_old_duels()
        return Response(200)
