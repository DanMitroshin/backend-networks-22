from drf_yasg import openapi

from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from collections import defaultdict

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import ParseError
from APIBackendService.views import AppAPIView
from Users.utils.permissions import check_has_content_access
from Users.serializers import (
    MainInfoUserSerializer,
    UserAccountGetSerializer,
)
from Users.models import User, UserAchievementRelation
from Users.utils import get_sale_info_for_user
from Users.utils.dialogs import get_dialog_index_for_user
from Statistics.models import InitLog, Achievement
from Statistics.utils import update_enters, get_new_achievements, get_last_init_timestamp, get_yesterday_progress
from re import fullmatch
from Users.constants import DEVICES
from Users.constants import REGISTRATION_PLATFORMS
from .auth import AuthView


class AccountProfileView(AppAPIView):
    # authentication_classes = []
    # permission_classes = []
    """
    Save and load account profile view
    """

    @swagger_auto_schema(
        operation_summary='Get all info',
        operation_description='Get user profile information',
        responses={
            200: 'OK',
        }
    )
    def get(self, request):
        user: User = request.user
        data = UserAccountGetSerializer(user).data

        editable_list = ['first_name', 'last_name', 'nickname', ]
        if user.registration_platform == REGISTRATION_PLATFORMS.VK:
            editable_list.append('email')

        data['editable'] = editable_list

        return Response(data)


# http://localhost:8000/api/history/user/information/user/main/
class UserMainInfoView(AppAPIView):
    """
    Get user main profile info
    """

    @swagger_auto_schema(
        operation_summary='Get user info',
        operation_description='Get user main profile information',
        responses={
            200: 'OK',
            400: 'Bad request',
        }
    )
    def get(self, request, ):
        return Response(MainInfoUserSerializer(request.user, context={
            'access': check_has_content_access(request.user)}).data)


#  last_version=10
# http://localhost:8000/api/user/init/
class InitView(AppAPIView):
    """
    Init view for entering the app
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Init view',
        operation_description='Init view: get main information, results, banners, dialogs, etc.',
        manual_parameters=[
            openapi.Parameter('device', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False,
                              description="Device"),
            openapi.Parameter('app_version', in_=openapi.IN_QUERY,
                              type=openapi.TYPE_INTEGER, required=True, ),
            openapi.Parameter('v', in_=openapi.IN_QUERY,
                              type=openapi.TYPE_INTEGER, required=False, ),
        ],
        responses={
            200: 'OK',
            400: 'Bad request',
        }
    )
    def get(self, request):

        answer = dict()
        user = request.user
        device = request.query_params.get("device", "a")

        if device == 'a':
            user.device = DEVICES.ANDROID
        elif device == 'i':
            user.device = DEVICES.APPLE

        app_version = int(request.query_params.get("app_version", -1))

        has_access_content = check_has_content_access(user)

        new_achievements = get_new_achievements(user, get_last_init_timestamp(user))
        info, achieve = update_enters(user, has_access_content=has_access_content)

        answer["yesterday_progress"] = dict()
        if "current" in info.keys():
            answer["yesterday_progress"] = get_yesterday_progress(user)

        answer["achievements"] = new_achievements + [achieve] if achieve else new_achievements
        answer["enters_info"] = info

        add_info_mass = []
        has_first_name = True
        if not user.first_name:
            add_info_mass.append({"value": "first_name", "label": "Имя", "now": ""})
            has_first_name = False
        if not user.last_name:
            add_info_mass.append({"value": "last_name", "label": "Фамилия", "now": ""})
        if not has_first_name:
            nickname = user.get_nickname()
            if fullmatch(r'id[0-9]+', nickname):
                add_info_mass.append({"value": "nickname", "label": "Никнейм", "now": nickname})
        if add_info_mass and user.registration_platform != REGISTRATION_PLATFORMS.APPLE_ID:
            answer["add_data"] = add_info_mass

        version = int(request.query_params.get('v', 0))

        InitLog.objects.create(version=version, title="-", user=user, device=device)
        amount_inits = InitLog.objects.filter(user=user).count()

        has_alert = False

        user.last_entry = timezone.datetime.utcnow()
        user.save(update_fields=['last_entry', 'device', 'version_app'])

        if app_version > 0 and (version >= 115 or user.device == DEVICES.APPLE) and not has_alert:
            try:
                dialog_id = get_dialog_index_for_user(user, app_version, amount_inits)
            except Exception as e:
                print("Err dialog:", e)
                dialog_id = None
            if type(dialog_id) == int:
                answer['dialogId'] = dialog_id

            try:
                if type(dialog_id) != int:
                    answer["saleOfferInfo"] = get_sale_info_for_user(user, amount_inits, has_access_content)
                else:
                    answer["saleOfferInfo"] = None
            except:
                pass
        return Response(answer)


class AchievementsView(AppAPIView):
    """
    User's achievements
    """

    @swagger_auto_schema(
        operation_summary='Get achievements',
        operation_description='Get user achievements',
        responses={
            200: 'OK',
            400: 'Bad request',
        }
    )
    def get(self, request):

        all_achievements = [{
            "id": a.id,
            "n": a.name,
            "d": a.description,
            "v": a.value,
            "c": a.category,
            "m": a.coins,
            "o": 0,
        } for a in Achievement.objects.all()]
        my_achievements = UserAchievementRelation.objects.filter(user=request.user.id)
        for my_achieve in my_achievements:
            for achieve in all_achievements:
                if my_achieve.achieve.id == achieve["id"]:
                    achieve["o"] = 1
                    break

        d = defaultdict(list)

        for i in all_achievements:
            d[i["c"]].append({
                "v": i["v"],
                "name": i["n"],
                "description": i["d"],
                "coins": i["m"],
                "is_open": i["o"]})

        return Response(d)
