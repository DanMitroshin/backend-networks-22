from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from APIBackendService.views import AppAPIView
from Services.utils.push_notifications import send_push_notification_to_user
from Users.models import NotificationPushToken


class NotificationTokenView(AppAPIView):

    def get(self, request):
        token = request.query_params['token']
        type_token = request.query_params.get('type', "expo")
        if token == 'undefined':
            return Response({"ok": True})

        item, created = NotificationPushToken.objects.update_or_create(
            user=request.user,
            token=token,
            type=type_token,
        )
        item.active = 1
        item.save()

        return Response({"ok": True})


class NotificationTokenInactiveView(AppAPIView):

    def get(self, request):
        token = request.query_params['token']
        NotificationPushToken.objects.filter(
            user=request.user,
            token=token,
        ).delete()
        return Response({"ok": True})


class NotificationsView(AppAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        params = request.query_params
        # print("Params")
        # print(params)
        token = params["token"]
        title = params["title"]
        body = params["body"]
        data = params["data"]
        # print("|> Title:", title)
        ans = send_push_notification_to_user(token, title, body, data=data)

        return Response(ans)
