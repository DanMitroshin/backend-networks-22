import json
from collections import defaultdict
from funcy import constantly
from .QUESTION_TYPES import *
from .DIALOG_STATUS import *
from .DIALOG_CATEGORY import *
from .CONTENT_TABLES import *
from .GENERATED_PRODUCT_TYPES import *
from .LESSON_TYPES import *

PRODUCT_MODEL_LESSON_TYPE_CHOICE = [
    (LESSON_TYPES.P0_UNLISTED_SUPPORTING_PRODUCT, 'Unlisted supporting products'),
    (LESSON_TYPES.P1_INFORMATIONAL_LESSON, 'Informational lesson'),
    (LESSON_TYPES.P2_HANDCRAFTED_TRAINER_LESSON, 'Handcrafted trainer lesson'),
    (LESSON_TYPES.P3_AUTOGENERATED_TRAINER_LESSON, 'Autogenerated trainer lesson')
]

BASE_LESSON_TYPE_CHOICE = [
    (LESSON_TYPES.P1_INFORMATIONAL_LESSON, 'Informational lesson'),
    (LESSON_TYPES.P2_HANDCRAFTED_TRAINER_LESSON, 'Handcrafted trainer lesson'),
    (LESSON_TYPES.P3_AUTOGENERATED_TRAINER_LESSON, 'Autogenerated trainer lesson')
]

ACCESS_GROUP_TYPES = (
    ('classroom', 'Classroom'),
    ('access', 'Content access group')
)

CLASSROOM_STUDENT_ACTIONS = tuple()
CLASSROOM_ASSISTENT_ACTIONS = ('add', 'remove') + CLASSROOM_STUDENT_ACTIONS
CLASSROOM_OWNER_ACTIONS = ('set_role', ) + CLASSROOM_ASSISTENT_ACTIONS

CLASSROOM_ACTIONS = CLASSROOM_OWNER_ACTIONS

CLASSROOM_ACTIONS_REQUIRED_FIELDS = defaultdict(constantly(tuple()))
CLASSROOM_ACTIONS_REQUIRED_FIELDS['set_role'] = ('role', )

CLASSROOM_ALLOWED_ACTIONS = defaultdict(constantly(tuple()))
CLASSROOM_ALLOWED_ACTIONS['classroom_assistent'] = CLASSROOM_ASSISTENT_ACTIONS
CLASSROOM_ALLOWED_ACTIONS['classroom_owner'] = CLASSROOM_OWNER_ACTIONS

TERMS = "TERMS"
DATES_RUS = "DATES_RUS"
DATES_WORLD = "DATES_WORLD"
PERSONS = "PERSONS"
MAPS = "MAPS"
ARCHITECTURE = "ARCHITECTURE"
LITERATURE = "LITERATURE"
PICTURES = "PICTURES"
SCULPTURE = "SCULPTURE"
THEORY = "THEORY"
QUESTIONS = "QUESTIONS"
PRACTISE = "PRACTISE"
VIDEOS = "VIDEOS"
HISTORY_TEXTS = "HISTORY_TEXTS"

TABLES_NAMES = [
    TERMS,
    DATES_RUS,
    PERSONS,
    MAPS,
    ARCHITECTURE,
    LITERATURE,
    PICTURES,
    SCULPTURE,
    THEORY,
    QUESTIONS,
    VIDEOS,
]


CONST_CONTENT_TABLE_NUMBERS = {
    TERMS: CONTENT_TABLES.TERMS,
    DATES_RUS: CONTENT_TABLES.DATES_RUS,
    PERSONS: CONTENT_TABLES.PERSONS,
    MAPS: CONTENT_TABLES.MAPS,
    ARCHITECTURE: CONTENT_TABLES.ARCHITECTURE,
    LITERATURE: CONTENT_TABLES.LITERATURE,
    PICTURES: CONTENT_TABLES.PICTURES,
    SCULPTURE: CONTENT_TABLES.SCULPTURE,
    HISTORY_TEXTS: CONTENT_TABLES.HISTORY_TEXTS,
    THEORY: CONTENT_TABLES.THEORY,
    QUESTIONS: CONTENT_TABLES.QUESTIONS,
    VIDEOS: CONTENT_TABLES.VIDEOS,
    DATES_WORLD: CONTENT_TABLES.DATES_WORLD,
}


class CLASS_CONTENT_TABLE_NAMES(object):
    TERMS = TERMS
    DATES_RUS = DATES_RUS
    PERSONS = PERSONS
    MAPS = MAPS
    ARCHITECTURE = ARCHITECTURE
    LITERATURE = LITERATURE
    PICTURES = PICTURES
    SCULPTURE = SCULPTURE
    THEORY = THEORY
    QUESTIONS = QUESTIONS
    VIDEOS = VIDEOS


CONTENT_TABLE_ACCESS_AMOUNT_LIMITS = {
    TERMS: 110,
    DATES_RUS: 100,
    ARCHITECTURE: 15,
    SCULPTURE: 15,
    LITERATURE: 9,
    PERSONS: 40,
    MAPS: 100,
    PICTURES: 15,
}

CONTENT_TABLE_ACCESS_INDEX_LIMITS = {
    TERMS: 110000,
    DATES_RUS: 80000,
    PERSONS: 41000,
    MAPS: 10000,
    ARCHITECTURE: 16000,
    LITERATURE: 10000,
    PICTURES: 16000,
    SCULPTURE: 14000,
}


class CLASS_CONTENT_TABLE_ACCESS_INDEX_LIMITS(object):
    TERMS = 110000
    DATES_RUS = 80000
    PERSONS = 41000
    MAPS = 10000
    ARCHITECTURE = 16000
    LITERATURE = 10000
    PICTURES = 16000
    SCULPTURE = 14000
    THEORY = -1  # INFINITY
    QUESTIONS = -1  # INFINITY
    VIDEOS = 0


SEARCH_TABLES_NAMES = [
    TERMS,
    DATES_RUS,
    PERSONS,
    MAPS,
    ARCHITECTURE,
    LITERATURE,
    PICTURES,
    SCULPTURE,
    THEORY,
    VIDEOS,
]

RUSSIAN_TABLES_NAMES = {
    TERMS: "Термины",
    DATES_RUS: "Даты истории России",
    PERSONS: "Личности",
    MAPS: "Карты",
    ARCHITECTURE: "Архитектура",
    LITERATURE: "Литература",
    PICTURES: "Картины",
    SCULPTURE: "Скульптура",
    THEORY: "Теория",
    QUESTIONS: "Вопросы",
}

CONTENT_TYPES = {

}

NAME = "name"
INDEX = "index"
INFORMATION = "information"
DEFINITION = "definition"
DATE = "date"
IMAGE = "image"
TAGS = "tags"
AUTHOR = "author"
CITY = "city"

TABLE = "table"
ITEMS = "items"
TEXT = "text"
LESSONS = "lessons"

AS_OBJECTS = "as_objects"


class PARAMS:
    NAME = NAME
    INDEX = INDEX
    INFORMATION = INFORMATION
    DATE = DATE
    IMAGE = IMAGE
    DEFINITION = DEFINITION
    TAGS = TAGS

    TABLE = TABLE
    ITEMS = ITEMS


LESSON_CRITERION = 300


def add_information(x, result):
    if x[INFORMATION]:
        if len(x[INFORMATION]) > LESSON_CRITERION:
            lessons = [{
                NAME: x[NAME],
                TEXT: x[INFORMATION],
                "key": 0
            }]
            result["detail"] = lessons  # blocks -> detail
        else:
            result[TEXT] += "\n\n" + x[INFORMATION]


def get_image_tag(uri, name):
    return f"<Image uri={uri}>{name}</Image>"


SUBTITLE = "subtitle"


def content_term(x):
    text = f"<b>{x[NAME]}</b> - {x['definition']}"
    result = {TEXT: text, NAME: x[NAME]}
    add_information(x, result)
    return result


def content_event(x):
    text = f"<b>Дата</b>: {x[DATE]}\n"
    text += f"<b>Событие</b>: {x[NAME]}"
    result = {TEXT: text, NAME: x[NAME]}
    add_information(x, result)
    return result


def content_person(x):
    text = f"<b>{x[NAME]}</b> - {x['summary']}"
    result = dict()
    result[NAME] = x[NAME]
    if x[IMAGE]:
        # text += f"\n{get_image_tag(x[IMAGE], x[NAME])}"
        result[IMAGE] = x[IMAGE]
    if x["dates_of_life"]:
        text += f"\n<b>Годы жизни</b>: {x['dates_of_life']}"
    if x["board_time"]:
        text += f"\n<b>Годы правления</b>: {x['board_time']}"
        result[SUBTITLE] = f"Годы правления: {x['board_time']}"
    result[TEXT] = text
    add_information(x, result)
    return result


def content_architecture(x):
    text = f"<b>Архитектура.</b> {x[NAME]}"
    # print(text)
    result = dict()
    result[NAME] = x[NAME]
    if x['style']:
        text += f"\n<b>Стиль</b>: {x['style']}"
    if x[IMAGE]:
        # text += f"\n{get_image_tag(x[IMAGE], x[NAME])}\n"
        result[IMAGE] = x[IMAGE]
    if x[DATE]:
        text += f"\n<b>Дата</b>: {x[DATE]}"
    if x['founder']:
        text += f"\n<b>Основатель</b>: {x['founder']}"
    if x['architect']:
        text += f"\n<b>Архитектор</b>: {x['architect']}"
        result[SUBTITLE] = f"Архитектор: {x['architect']}"
    if x[CITY]:
        text += f"\n<b>Город</b>: {x[CITY]}"
    # print("2222")
    result[TEXT] = text
    add_information(x, result)
    # print("3333333")
    return result


def content_sculpture(x):
    text = f"<b>Скульптура.</b> {x[NAME]}"
    result = dict()
    result[NAME] = x[NAME]
    if x[AUTHOR]:
        text += f"\n<b>Автор</b>: {x[AUTHOR]}"
        result[SUBTITLE] = f"Автор: {x[AUTHOR]}"
    if x[IMAGE]:
        # text += f"\n{get_image_tag(x[IMAGE], x[NAME])}\n"
        result[IMAGE] = x[IMAGE]
    if x[DATE]:
        text += f"\n<b>Дата</b>: {x[DATE]}"
    if x[CITY]:
        text += f"\n<b>Город</b>: {x[CITY]}"
    result[TEXT] = text
    add_information(x, result)
    return result


def content_literature(x):
    text = f"<b>Литература.</b> {x[NAME]}"
    result = dict()
    result[NAME] = x[NAME]
    if x[AUTHOR]:
        text += f"\n<b>Автор</b>: {x[AUTHOR]}"
    if x[DATE]:
        text += f"\n<b>Дата</b>: {x[DATE]}"
    result[TEXT] = text
    add_information(x, result)
    return result


def content_picture(x):
    text = f"<b>Живопись.</b> {x[NAME]}"
    result = dict()
    result[NAME] = x[NAME]
    if x[AUTHOR]:
        text += f"\n<b>Автор</b>: {x[AUTHOR]}"
        result[SUBTITLE] = f"Автор: {x[AUTHOR]}"
    if x[IMAGE]:
        # text += f"\n{get_image_tag(x[IMAGE], x[NAME])}\n"
        result[IMAGE] = x[IMAGE]
    if x[DATE]:
        text += f"\n<b>Дата</b>: {x[DATE]}"
    result[TEXT] = text
    add_information(x, result)
    return result


def content_map(x):
    text = f"<b>Историческая карта.</b> {x[NAME]}"
    result = dict()
    result[NAME] = x[NAME]
    if x[DATE]:
        text += f"\n<b>Дата</b>: {x[DATE]}"
        result[SUBTITLE] = f"Дата: {x[DATE]}"
    if x[IMAGE]:
        # text += f"\n{get_image_tag(x[IMAGE], x[NAME])}\n"
        result[IMAGE] = x[IMAGE]
    if x["task_image"]:
        text += f"\n{get_image_tag(x['task_image'], 'Карта с заданиями')}\n"
    result[TEXT] = text
    add_information(x, result)
    return result


CREATE_FULL_CONTENT_FUNCTIONS = {
    TERMS: content_term,
    DATES_RUS: content_event,
    ARCHITECTURE: content_architecture,
    SCULPTURE: content_sculpture,
    LITERATURE: content_literature,
    PERSONS: content_person,
    MAPS: content_map,
    PICTURES: content_picture,
    THEORY: "",
    QUESTIONS: "",
    VIDEOS: lambda x: {'text': ""},
}


def get_common_str(s, may_be_empty_str):
    if may_be_empty_str:
        return f"{s}{may_be_empty_str}"
    return ""


def preview_string(x: str, size=120) -> str:
    if len(x) < size:
        return x
    x = x[:size].strip()
    ind = x.rfind(' ')
    # print("|>> IND SPACE", ind)
    if ind > 0:
        x = x[:ind].strip() + "..."
    return x


def get_short_block_str(text):
    short_str = f"{preview_string(text, size=200)}"
    short_str = short_str.replace('\n\n', '\n').replace('\n', '. ')
    return short_str


def preview_lesson(x):
    # print(str(x))
    res = f"<b>Урок: {x[NAME]}</b>"
    if len(x["blocks"]) > 0:
        short_str = get_short_block_str(x['blocks'][0]['text'])
        res += f"\n{short_str}"
    return res


def preview_lesson_description(x):
    # print(str(x))
    res = f""
    if len(x["blocks"]) > 0:
        short_str = get_short_block_str(x['blocks'][0]['text'])
        res += short_str
    return res


def preview_question(x):
    s = json.dumps(x)
    open_tag_char = "%o%"
    end_tag_char = "%e%"
    s = s.replace('<', open_tag_char).replace('>', end_tag_char)
    return f"<QUESTION open={open_tag_char} end={end_tag_char}>{s}</QUESTION>"


def get_may_be_image(image, name):
    if image:
        return get_image_tag(image, name + ".")
    return ""


CREATE_PREVIEW_FUNCTIONS = {
    TERMS: lambda x: f"<b>{x[NAME]}</b> - {x['definition']}",
    DATES_RUS: lambda x: f"<b>{x[DATE]}</b>\n{x[NAME]}",
    ARCHITECTURE: lambda x: f"<b>{x[NAME]}</b>\n{get_common_str('Архитектор ', x['architect'])}",  # \n{get_may_be_image(x['image'], x[NAME])}
    SCULPTURE: lambda x: f"<b>{x[NAME]}</b>\n{get_common_str('Автор ', x[AUTHOR])}",
    LITERATURE: lambda x: f"<b>{x[NAME]}</b>\n{get_common_str('Автор ', x[AUTHOR])}",
    PERSONS: lambda x: f"<b>{x[NAME]}</b>{get_common_str(' - ', x['summary'])}",
    MAPS: lambda x: f"{x[NAME]}",
    PICTURES: lambda x: f"<b>{x[NAME]}</b>\n{get_common_str('Автор ', x[AUTHOR])}",
    THEORY: lambda x: preview_lesson(x),
    VIDEOS: lambda x: f"<b>Видео.</b> {x[NAME]}",
    QUESTIONS: lambda x: preview_question(x), #lambda x: f"<b>Вопрос</b>: {preview_question(x['question'])}",
}


class CLASS_CONTENT_WIKI_PREVIEW_FUNCTIONS(object):
    TERMS = CREATE_PREVIEW_FUNCTIONS[TERMS]
    DATES_RUS = CREATE_PREVIEW_FUNCTIONS[DATES_RUS]
    ARCHITECTURE = CREATE_PREVIEW_FUNCTIONS[ARCHITECTURE]
    SCULPTURE = CREATE_PREVIEW_FUNCTIONS[SCULPTURE]
    LITERATURE = CREATE_PREVIEW_FUNCTIONS[LITERATURE]
    PERSONS = CREATE_PREVIEW_FUNCTIONS[PERSONS]
    MAPS = CREATE_PREVIEW_FUNCTIONS[MAPS]
    PICTURES = CREATE_PREVIEW_FUNCTIONS[PICTURES]
    THEORY = CREATE_PREVIEW_FUNCTIONS[THEORY]
    VIDEOS = CREATE_PREVIEW_FUNCTIONS[VIDEOS]
    QUESTIONS = CREATE_PREVIEW_FUNCTIONS[QUESTIONS]


CREATE_PREVIEW_DESCRIPTION_FUNCTIONS = {
    TERMS: lambda x: f"{x['definition']}",
    DATES_RUS: lambda x: f"{x[DATE]}",
    ARCHITECTURE: lambda x: f"{get_common_str('<b>Архитектор</b> ', x['architect'])}",  # \n{get_may_be_image(x['image'], x[NAME])}
    SCULPTURE: lambda x: f"{get_common_str('<b>Автор</b> ', x[AUTHOR])}",
    LITERATURE: lambda x: f"{get_common_str('<b>Автор</b> ', x[AUTHOR])}",
    PERSONS: lambda x: f"{get_common_str('', x['summary'])}",
    MAPS: lambda x: f"",
    PICTURES: lambda x: f"{get_common_str('<b>Автор</b> ', x[AUTHOR])}",
    THEORY: lambda x: preview_lesson_description(x),
    VIDEOS: lambda x: f"",
    QUESTIONS: lambda x: preview_question(x), #lambda x: f"<b>Вопрос</b>: {preview_question(x['question'])}",
}