from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ParseError

from Content.constants import RUSSIAN_TABLES_NAMES, TABLES_NAMES, VIDEOS, ITEMS
from Content.models import ContentIndexRelationship
from Content.serializers import CONTENT_WIKI_PREVIEW_SERIALIZERS
from Content.utils.wiki_content import get_code_from_table, get_table_for_code, TABLES

from Content.constants import CREATE_FULL_CONTENT_FUNCTIONS, TERMS, \
    DATES_RUS, ARCHITECTURE, LITERATURE, VIDEOS, SCULPTURE, PERSONS, PICTURES, THEORY, MAPS, QUESTIONS, \
    RUSSIAN_TABLES_NAMES, TABLES_NAMES


def get_preview_related_objects_for_item(
        table, index, user_access
):
    code = get_code_from_table(table)
    # print("|> Code:", code)
    relations = ContentIndexRelationship.objects.filter(
        first_code=code,
        first_index=index,
        # second_code=
    )

    MAX_VALUE = 3

    counters = {
        TERMS: 0,
        DATES_RUS: 0,
        ARCHITECTURE: 0,
        SCULPTURE: 0,
        LITERATURE: 0,
        PERSONS: 0,
        MAPS: 0,
        PICTURES: 0,
        THEORY: 0,
        QUESTIONS: 0,
        VIDEOS: 0,
    }

    related_objects = {
        TERMS: [],
        DATES_RUS: [],
        ARCHITECTURE: [],
        SCULPTURE: [],
        LITERATURE: [],
        PERSONS: [],
        MAPS: [],
        PICTURES: [],
        THEORY: [],
        QUESTIONS: [],
        VIDEOS: []
    }

    video_id = -1

    for relation in relations:
        try:
            table_relation = get_table_for_code(relation.second_code)
            if table_relation == VIDEOS:
                # print("VIDEO!!!!!")

                video_id = relation.second_index
                continue
            # print("RELATION")
            if counters[table_relation] + 1 <= MAX_VALUE:
                new_item_obj = get_object_or_404(TABLES[table_relation], index=relation.second_index)
                new_item = CONTENT_WIKI_PREVIEW_SERIALIZERS[table_relation](
                    new_item_obj, context={'access': user_access}).data
                related_objects[table_relation].append(
                    new_item
                    # get_preview_object_by_index_and_table(
                    #     relation.second_index,
                    #     table_relation
                    # )
                )
            counters[table_relation] += 1
        except Exception as e:
            print("|> ERROR FOR", e)
            continue

    # print("|> GET RELATIONS!")

    answer = {
        "index": index,
        "relations_amount": sum([counters[key] for key in counters]),
        # "relation_tags": [f"{item.second_code}{item.second_index}" for item in relations],
        "relations": [
            {
                "table": table,
                "name": RUSSIAN_TABLES_NAMES[table],
                "objects": related_objects[table],
                "more": counters[table] - len(related_objects[table]),
            } for table in TABLES_NAMES if len(related_objects[table]) > 0
        ]
    }

    # print("GET ANSWER!")

    if video_id > 0:
        answer["videoId"] = video_id

    return answer


def update_content_relations(data):

    for item in data[ITEMS]:
        first_code = item[0][:2]
        first_index = int(item[0][2:])
        second_code = item[1][:2]
        second_index = int(item[1][2:])
        # print("|> INFO:", first_code, first_index, second_code, second_index)

        relations = ContentIndexRelationship.objects.filter(
            first_code=first_code,
            first_index=first_index,
            second_code=second_code,
            second_index=second_index,
        )
        if relations.exists():
            continue
        else:
            ContentIndexRelationship.objects.create(
                first_code=first_code,
                first_index=first_index,
                second_code=second_code,
                second_index=second_index,
            )
