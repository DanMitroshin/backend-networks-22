from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication

from APIBackendService.views import AppAPIView
from Content.utils.life_hacks import get_history_texts_list, get_history_text_by_index
from Users.utils.permissions import IsCards


class CardsAccessView(AppAPIView):
    """
    Test cards view.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsCards]

    def get(self, request):
        return Response({"result": True})


# http://localhost:8000/api/content/content/get/historyTexts/
class HistoryTextView(AppAPIView):
    """
    History texts. 2 actions:
    1. list - get list of items
    2. item - get item info
    """
    @swagger_auto_schema(
        operation_summary='History texts',
        operation_description='History texts',
        manual_parameters=[
            openapi.Parameter('action', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="list/item"),
            openapi.Parameter('index', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False,
                              description="Only for item action"),
        ],
        responses={
            200: 'OK',
            400: 'Bad request',
            403: 'Not permitted',
        }
    )
    def get(self, request):
        params = request.query_params
        user = request.user
        action = params['action']  # ['list', 'item']

        if action == 'list':
            return Response(get_history_texts_list(user))

        index = int(params['index'])
        return Response(get_history_text_by_index(user, index))
