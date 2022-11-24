from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication

from APIBackendService.views import AppAPIView
from Content.utils.dialog_actions import get_dialog, save_user_dialog_choices, add_dialog, get_statistics_answers_dialog


class DialogView(AppAPIView):
    """
    Dialog view for get dialog configuration and save answers
    URL to test: http://localhost:8000/api/history/content/dialogs/
    """

    @swagger_auto_schema(
        operation_summary='Dialog config',
        operation_description='Dialog config',
        manual_parameters=[
            openapi.Parameter('index',
                              in_=openapi.IN_QUERY,
                              type=openapi.TYPE_INTEGER,
                              description="Dialog index"),
        ],
        responses={
            200: 'OK',
            400: 'Bad request',
            404: 'Dialog not found',
            403: 'Not permitted',
        }
    )
    def get(self, request):
        index = int(request.query_params['index'])
        return Response(get_dialog(index, user=request.user))

    @swagger_auto_schema(
        operation_summary='Dialog answers saver',
        operation_description='Dialog answers saver',
        manual_parameters=[
            openapi.Parameter('index', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description="Dialog index"),
            openapi.Parameter('actions', in_=openapi.IN_QUERY, type=openapi.TYPE_ARRAY,
                              items=openapi.Schema(type=openapi.TYPE_INTEGER),
                              description="Dialog answers [buttons indexes]"),
        ],
        responses={
            200: 'OK',
            400: 'Bad request',
            404: 'Dialog not found',
            403: 'Not permitted',
        }
    )
    def post(self, request):
        # print("ACTIONS:", request.data['actions'])
        index = request.data['index']
        actions = request.data['actions']
        user = request.user
        save_user_dialog_choices(user, index, actions)
        return Response(200)


class SaveDialog(APIView):
    """
    Admins only.
    URL for test: http://localhost:8000/api/content/dialogs/save/
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        dialog = request.data
        add_dialog(**dialog)
        return Response(200)


class DialogStatisticsAnswers(AppAPIView):
    """
    Admins only.
    URL for test: http://localhost:8000/api/history/content/dialogs/statistics/answers/
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        index = int(request.GET.get('index', 50))
        get_statistics_answers_dialog(index)
        return Response(200)
