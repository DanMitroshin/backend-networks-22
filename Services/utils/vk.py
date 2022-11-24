def check_image_in_message(message_object: dict):
    try:
        if 'attachments' not in message_object:
            return None
        attachments: list = message_object.get('attachments')
        for attachment in attachments:
            if attachment.get("type", "") == "photo":
                photo_attachment = attachment['photo']
                if photo_attachment.get('photo_1280', ""):
                    return photo_attachment.get("photo_1280")
                if photo_attachment.get('photo_807', ""):
                    return photo_attachment.get("photo_807")
        return None
    except:
        return None
