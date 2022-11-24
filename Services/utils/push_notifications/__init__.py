import requests
from time import sleep
from django.db.models import Max, Min
from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)

from Users.models import NotificationPushToken
from Statistics.models import InitLog


def send_push_notification_to_user(token, title, body="", data=None, ttl=0):
    response = {}
    success = 'success'
    identifier = "identifier"
    answer = {success: False}
    try:
        response = PushClient().publish(
            PushMessage(to=token,
                        title=title,
                        body=body,
                        data=data,
                        ttl=ttl
                        ))
        answer[success] = True
    except PushServerError as exc:
        # Encountered some likely formatting/validation error.
        pass
        # print("|> PushServerError:", exc)
    except:
        # print("|> Unknown connection error")
        pass

    try:
        # We got a response back, but we don't know whether it's an error yet.
        # This call raises errors so we can handle them with normal exception
        # flows.
        response.validate_response()
        # print("Response", response)
        # print("|> Notification identifier:", response.id)
        answer["result"] = response
    except DeviceNotRegisteredError:
        pass
        # Mark the push token as inactive
        # from notifications.models import PushToken
        NotificationPushToken.objects.filter(token=token).update(active=0)
    except:
        pass

    # print("|> Get answer for push request:", answer)
    return answer


def send_notification(to, title, body, data=None):
    def send():
        response = requests.post("https://exp.host/--/api/v2/push/send/",
                                 # headers={'Content-Type': 'application/json'},
                                 json={'to': to,
                                       'title': title,
                                       'body': body,
                                       'data': {} if data is None else data},
                                 )
        js = response.json()
        # print("JS:", js)
        return js

    try:
        return send()
    except Exception as e:
        sleep_seconds = 8
        # print("|> Send notification to server EXPO error:", e)
        # print(f"|> Sleep {sleep_seconds} seconds...")
        sleep(sleep_seconds)
        return send()


def send_notification_by_array(array):
    def send():
        response = requests.post(
            "https://exp.host/--/api/v2/push/send/",
            # headers={'Content-Type': 'application/json'},
            json=array,
        )
        js = response.json()
        # print("JS:", js)
        return js

    try:
        return send()
    except Exception as e:
        sleep_seconds = 8
        # print("|> Send notification to server EXPO error:", e)
        # print(f"|> Sleep {sleep_seconds} seconds...")
        sleep(sleep_seconds)
        return send()


def get_tokens_by_user(user):
    tokens = NotificationPushToken.objects.filter(user=user)
    return tokens


def delete_unused_tokens(tokens, request_data):
    # print(f"Js {js}")
    counter = 0
    deleted = 0
    try:
        for token in request_data["data"]:
            try:
                if token["status"] == "error":
                    if token["details"]["error"] == "DeviceNotRegistered":
                        # print(f"Delete {counter}")
                        deleted += 1
                        NotificationPushToken.objects.filter(token=tokens[counter]).delete()
            except Exception as e:
                pass
                # print("|> Error processing expo answer:", e)
            counter += 1
    except Exception as e:
        pass
        # print("|> Error while deleting unused tokens:", e)
    return counter - deleted


def send_notification_by_user(user, title, body, data=None, version=-1):
    tokens = get_tokens_by_user(user)
    if version >= 0:
        try:
            max_version = InitLog.objects.filter(user=user).aggregate(Max('version'))['version__max']  # from
            if version <= max_version:
                return
        except Exception as e:
            max_version = 0

        if version <= max_version:
            return

    to = []
    for token in tokens:
        to.append(token.token)
    js = send_notification(to, title, body, data)
    delete_unused_tokens(to, js)
    return js


def send_notification_by_list_of_tokens(
        tokens, title, body, data=None, version=-1, show_logs=False):
    to = []
    try:
        for token in tokens:
            try:
                if version < 0:
                    to.append(token.token)
                    continue
                max_version = InitLog.objects.filter(user=token.user).aggregate(Max('version'))[
                    'version__max'
                ]
                if max_version < version:
                    to.append(token.token)
                # print("|> Max version:", max_version)
            except Exception as e:
                # print("|> Version__max error:", e)
                max_version = 0
                if max_version < version:
                    to.append(token.token)
    except Exception as e:
        pass
        # print("|> Error in circle tokens:", e)

    send_amount = 0
    if show_logs:
        print(f"|> Use {len(to)} tokens with {len(to) // 100 + 1} iterations")
    for i in range(len(to) // 100 + 1):
        try:
            # print("|> Iteration:", i, end='...')
            sleep(5)
            send_to = to[i * 100: (i + 1) * 100]
            js = send_notification(send_to, title, body, data)
            local_send_amount = delete_unused_tokens(send_to, js)
            send_amount += local_send_amount
            if show_logs:
                print(f" delete {len(send_to) - local_send_amount} tokens, send {local_send_amount} messages")
        except Exception as e:
            # print("|> Error in main 'for' while sending messages:", e)
            continue

    return send_amount


def send_notification_to_all_users(title, body, data=None, version=-1):
    tokens = NotificationPushToken.objects.all()  # .filter(token="ExponentPushToken[f3XFMiARve8HJM1bG7GhBK]")
    return send_notification_by_list_of_tokens(tokens, title, body, data=data, version=version)


def send_notification_to_users(users, title, body, data=None, version=-1):
    tokens = NotificationPushToken.objects.filter(user__in=users)
    return send_notification_by_list_of_tokens(tokens, title, body, data=data, version=version)


def send_different_notifications_by_info_list(info: list):
    send_list = []
    total_tokens_amount = 0
    for message in info:
        tokens = NotificationPushToken.objects.filter(user=message['user'])
        user_tokens_amount = tokens.count()
        if user_tokens_amount == 0:
            continue
        total_tokens_amount += user_tokens_amount
        if user_tokens_amount == 1:
            to = tokens.first().token
        else:
            to = [token.token for token in tokens]
        send_list.append({
            'to': to,
            'title': message['title'],
            'body': message['body'],
            'data': {} if 'data' not in message.keys() else message['data'],
        })
    # print(f"|> Use {total_tokens_amount} tokens with minimum {total_tokens_amount // 100 + 1} iterations")

    counter = 0
    send_amount = 0
    total_send_amount = 0
    border = 100
    local_really_send_amount = 0
    i = 0

    while True:
        try:
            i += 1
            send_tokens = []
            if counter >= len(send_list):
                break
            local_send_list = []
            local_send_amount = 0
            while True:
                if counter >= len(send_list):
                    if len(local_send_list) > 0:
                        total_send_amount += local_send_amount
                        try:
                            js = send_notification_by_array(local_send_list)
                            local_really_send_amount = delete_unused_tokens(send_tokens, js)
                        except Exception as e:
                            pass
                            # print("|> Send error:", e)
                    break
                tokens = send_list[counter]['to']
                new_len_tokens = 1 if type(tokens) == str else len(tokens)
                if new_len_tokens + local_send_amount < border:
                    local_send_amount += new_len_tokens
                    local_send_list.append(send_list[counter])
                    counter += 1
                    if type(tokens) == str:
                        send_tokens.append(tokens)
                    else:
                        for token in tokens:
                            send_tokens.append(token)
                else:
                    # print(f"|> Send to {local_send_amount})")
                    total_send_amount += local_send_amount
                    try:
                        js = send_notification_by_array(local_send_list)
                        local_really_send_amount = delete_unused_tokens(send_tokens, js)
                    except Exception as e:
                        pass
                        # print("|> Send error:", e)
                    break

            sleep(5)
            send_amount += local_really_send_amount
        except Exception as e:
            continue

    return send_amount
