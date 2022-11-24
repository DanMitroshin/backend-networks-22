from Content.models import ContentHistoryText
from Users.utils.permissions import check_has_life_hack_documents_access
from rest_framework.exceptions import PermissionDenied

BORDER_INDEX_ACCESS = 350


def get_history_texts_list(
        user,
):
    has_access = check_has_life_hack_documents_access(user)
    result = dict()
    array = []
    for text in ContentHistoryText.objects.all():
        array.append({
            'name': text.name,
            'index': text.index,
            'access': has_access or text.index < BORDER_INDEX_ACCESS,
        })
    result['texts'] = array
    return result


def get_history_text_by_index(
        user, index
):
    BORDER_INDEX_ACCESS = 350
    has_access = check_has_life_hack_documents_access(user)

    if has_access or index < BORDER_INDEX_ACCESS:
        text = ContentHistoryText.objects.filter(index=index).first()
        result = {
            'text': text.text,
            'name': text.name,
            'date': text.date,
            'information': text.information,
            'is_full': text.is_full,
            'recognize_hint': text.recognize_hint,
        }
        return result
    else:
        raise PermissionDenied()
