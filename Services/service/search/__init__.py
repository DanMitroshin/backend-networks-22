from .api import (
    search_full_data, search_name,
    search_entity_name, search_full_data_entity,
    add_name_to_index, add_full_document_to_index, add_name_to_entity_index, add_full_document_to_entity_index,
    add_names_to_index, add_full_documents_to_index)
from Content.serializers import ContentWikiPreviewSerializer
from Content.utils.wiki_content import get_wiki_content_table, check_table_in_wiki_tables, LIST_WIKI_TABLES
from Users.utils.permissions import check_has_content_access
from math import ceil


def search_full_content_objects_in_table(
        user, q, table, offset=0,
):
    has_access = check_has_content_access(user)
    content_table = get_wiki_content_table(table)

    search_results = search_full_data(q, table, offset=offset)
    limit = search_results["limit"]
    offset = search_results["offset"]
    count = search_results["nbHits"]
    pages = ceil(count / limit) if limit > 0 else 0

    def get_next_offset():
        if offset + limit >= count:
            return None
        return offset + limit

    def get_previous_offset():
        if offset - limit < 0:
            return None
        return offset - limit

    answer = {
        'links': {
            'next': {
                # 'link': self.get_next_link(),
                'offset': get_next_offset(),
            },
            'previous': {
                # 'link': self.get_previous_link(),
                'offset': get_previous_offset(),
            },
        },
        'limit': limit,
        'offset': search_results["offset"],
        'count': count,
        'pages': pages,
        # 'nbHits': search_results["nbHits"],
        'data': [],
    }

    # preview_function = CREATE_PREVIEW_FUNCTIONS[table]

    indexes = list(map(lambda x: x["index"], search_results["hits"]))
    queryset = content_table.objects.filter(index__in=indexes)
    serializer = ContentWikiPreviewSerializer(
        queryset,
        many=True,
        context={
            "access": has_access,
            "table": table,
        }
    )

    # table_limit = SEARCH_TABLES_LIMITS[table]
    # if not has_access and table_limit > 0:
    #     indexes = list(filter(lambda x: x < table_limit, indexes))
    #     answer["close"] = search_results["nbHits"] - len(indexes)
    #
    # for item in ContentTable.objects.filter(index__in=indexes):
    #     # if table not in [QUESTIONS, THEORY, VIDEOS]: !!!!
    #     try:
    #         d = item.__dict__
    #         data = {key: d[key] for key in d.keys() if key not in ["_state", "id"]}
    #         answer['hits'].append({
    #             "text": preview_function(data),
    #             "index": item.index,
    #             NAME: data[NAME],
    #         })
    #     except Exception as e:
    #         print("Err", e)

    answer.update({'data': serializer.data})

    return answer


def reformat_search_names_output(search_results):
    def search_item_processing(item):
        return {
            'type': 'text',
            'index': item.get("index", None),
            'text': item.get("name", ""),
        }

    limit = search_results["limit"]
    offset = search_results["offset"]
    count = search_results["nbHits"]
    pages = ceil(count / limit) if limit > 0 else 0

    result = {
        'count': count,
        'offset': offset,
        'limit': limit,
        'pages': pages,
        'data': list(map(search_item_processing, search_results.get("hits", [])))
    }

    return result


def search_content_object_names_in_table(
        q, table,
):
    check_table_in_wiki_tables(table)

    return reformat_search_names_output(
        search_name(
            q,
            table,
            # options={'attributesToHighlight': ['*']}
        )
    )


def add_all_data_from_tables_to_search_indexes():
    """
    One-time function for adding all information to search index
    :return: None
    """
    for TABLE_NAME in LIST_WIKI_TABLES.keys():
        content_table = LIST_WIKI_TABLES[TABLE_NAME]
        items = list(content_table.objects.all().values())
        # print(items[:3])
        # break
        print("|> TABLE:", TABLE_NAME, "| add items... ", end="")
        add_full_documents_to_index(items, table=TABLE_NAME)
        add_names_to_index(items, table=TABLE_NAME)
        print("done")
