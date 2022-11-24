import datetime
from django.core.management.base import BaseCommand

from Services.service import alert_admin_message


class AppSafeCommand(BaseCommand):
    def execute(self, *args, **options):
        try:
            return super().execute(*args, **options)
        except Exception as e:
            def sp(s):
                return str(s)
                # return str(s).replace('_', '\\_')

            text = f"🆘 Ошибка в выполнении Command\n\n" \
                   f"<b>Class</b>: {sp(self.__class__.__name__)}\n" \
                   f"<b>UTC</b>: {sp(datetime.datetime.utcnow())}\n" \
                   f"<b>Error type</b>: {sp(e.__class__.__name__)}\n" \
                   f"<b>Error</b>: {sp(e)}"

            alert_admin_message(text, parse_mode='HTML')
            raise e
