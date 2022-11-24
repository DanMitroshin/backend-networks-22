from .telegram_bot import alert_message


def alert_admin_message(text, parse_mode='HTML'):
    alert_message(text, parse_mode=parse_mode)
