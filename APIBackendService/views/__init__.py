from rest_framework import exceptions, viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
import datetime

from Services.service import alert_admin_message
from django.conf import settings


class BaseAppAPIView(APIView):
    """
    Base APIView for app with:
     - alert about exceptions
     - ...
    """

    def handle_exception(self, exc):

        if isinstance(exc, (exceptions.APIException, )):
            return super().handle_exception(exc)

        try:
            try:
                if self.request.method == "GET":
                    params = "(in query)"  # str(self.request.query_params.dict())
                else:
                    params = str(self.request.data)
                if len(params) > 200:
                    params = params[:200] + "..."
            except Exception as e:
                params = f"‼ Ошибка получения параметров запроса: {e}"

            def string_process(s):
                return str(s)  # .replace('_', '\\_')

            user = string_process(self.request.user)
            err = string_process(exc)
            path = string_process(self.request.get_full_path())

            text = f"🆘 Ошибка в выполнении View\n\n" \
                   f"<b>Method</b>: {self.request.method}\n" \
                   f"<b>Path</b>: {settings.CURRENT_DOMAIN}{path}\n" \
                   f"<b>Data</b>: {string_process(params)}\n" \
                   f"<b>Class</b>: {string_process(self.__class__.__name__)}\n" \
                   f"<b>UTC</b>: {string_process(datetime.datetime.utcnow())}\n" \
                   f"<b>User</b>: {user}\n" \
                   f"<b>Error type</b>: {string_process(exc.__class__.__name__)}\n" \
                   f"<b>Error</b>: {err}"

            # print(text)
            alert_admin_message(text)
        except:
            pass

        return super().handle_exception(exc)


class BaseAppReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
    """
        Base ReadOnlyModelViewSet for app with:
         - alert about exceptions
         - ...
        """

    def handle_exception(self, exc):

        if isinstance(exc, (exceptions.APIException,)):
            return super().handle_exception(exc)

        try:
            try:
                if self.request.method == "GET":
                    params = "(in query)"  # str(self.request.query_params.dict())
                else:
                    params = str(self.request.data)
                if len(params) > 200:
                    params = params[:200] + "..."
            except Exception as e:
                params = f"‼ Ошибка получения параметров запроса: {e}"

            def string_process(s):
                return str(s)  # .replace('_', '\\_')

            try:
                user_str = self.request.user
            except:
                user_str = "*anon*"

            user = string_process(user_str)
            err = string_process(exc)
            path = string_process(self.request.get_full_path())

            text = f"🆘 Ошибка в выполнении ReadOnlyModelViewSet\n\n" \
                   f"<b>Method</b>: {self.request.method}\n" \
                   f"<b>Path</b>: {settings.CURRENT_DOMAIN}{path}\n" \
                   f"<b>Data</b>: {string_process(params)}\n" \
                   f"<b>Class</b>: {string_process(self.__class__.__name__)}\n" \
                   f"<b>UTC</b>: {datetime.datetime.utcnow()}\n" \
                   f"<b>User</b>: {user}\n" \
                   f"<b>Error type</b>: {string_process(exc.__class__.__name__)}\n" \
                   f"<b>Error</b>: {err}"

            # print(text)
            alert_admin_message(text)
        except:
            pass

        return super().handle_exception(exc)


class AppAPIView(BaseAppAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
