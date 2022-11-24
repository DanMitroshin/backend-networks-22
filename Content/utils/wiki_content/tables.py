from rest_framework.exceptions import ParseError

from Content.constants import (
    TERMS,
    DATES_RUS,
    PRACTISE,
    # DATES_WORLD,
    HISTORY_TEXTS,
    PERSONS,
    PICTURES, THEORY, QUESTIONS, VIDEOS,
    MAPS,
    SCULPTURE,
    ARCHITECTURE,
    LITERATURE,
    TABLES_NAMES)

from Content.models import (
    Product,
    TrainerBlock,
    ContentEvent,
    ContentArchitecture,
    ContentLiterature,
    ContentMap,
    ContentPerson,
    ContentPicture,
    ContentSculpture,
    ContentTerm,
    ContentVideo,
    ContentHistoryText,
)


TABLES = {
    TERMS: ContentTerm,
    DATES_RUS: ContentEvent,
    ARCHITECTURE: ContentArchitecture,
    SCULPTURE: ContentSculpture,
    LITERATURE: ContentLiterature,
    PERSONS: ContentPerson,
    MAPS: ContentMap,
    PICTURES: ContentPicture,
    THEORY: Product,
    QUESTIONS: TrainerBlock,
    PRACTISE: Product,
    VIDEOS: ContentVideo,
    HISTORY_TEXTS: ContentHistoryText,
}


LIST_WIKI_TABLES = {
    TERMS: ContentTerm,
    DATES_RUS: ContentEvent,
    ARCHITECTURE: ContentArchitecture,
    SCULPTURE: ContentSculpture,
    LITERATURE: ContentLiterature,
    PERSONS: ContentPerson,
    MAPS: ContentMap,
    PICTURES: ContentPicture,
    VIDEOS: ContentVideo,
    THEORY: Product,
    HISTORY_TEXTS: ContentHistoryText,
}


# WIKI ###########
def check_table_in_wiki_tables(table):
    if table not in LIST_WIKI_TABLES.keys():
        raise ParseError(detail="Bad table name")


def get_wiki_content_table(table):
    check_table_in_wiki_tables(table)
    return LIST_WIKI_TABLES[table]


# ALL CONTENT #######
def check_table_in_content_tables(table):
    if table not in TABLES.keys():
        raise ParseError(detail="Bad table name")


def get_content_table(table):
    check_table_in_content_tables(table)
    return TABLES[table]


def get_table_for_code(code):
    for table in TABLES_NAMES:
        if code == table[:2]:
            return table
    return ""


def get_code_from_table(table):
    # if table == DATES_RUS:
    #     return "DR"
    # if table == DATES_WORLD:
    #     return "DW"
    return table[:2]
