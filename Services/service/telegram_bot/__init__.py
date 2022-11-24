import telebot


TOKEN = "<TG-TOKEN>"
chat_id = -12345


def alert_message(text, parse_mode="Markdown"):
    try:
        bot = telebot.TeleBot(TOKEN)
        text = text.strip()
        bot.send_message(chat_id, text=text, parse_mode=parse_mode)
    except Exception as e:
        print("Error message", e)
