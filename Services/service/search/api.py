import meilisearch
import re
from meilisearch.errors import MeiliSearchApiError
from django.conf import settings


MEILI_MASTER_KEY = settings.MEILI_MASTER_KEY
MEILISEARCH_ADDRESS = settings.MEILISEARCH_ADDRESS
HISTORY_THEME = "HISTORY"


def normalize_text(text):
    def create_words_info_array(phrase: str):
        word_get_pattern = r'\w+'
        result = re.finditer(word_get_pattern, phrase.lower(), flags=re.IGNORECASE)
        words = []
        for match in result:
            word = match.group()
            words.append(word)
#             word_forms = set([word] + list(map(lambda x: x.normal_form, morph.parse(word))))
        return words

    text = re.sub(r'<\w+[^>]*>', '', text)
    text = re.sub(r'</\w+[^>]*>', '', text)
    text = text.lower()
    text = text.replace('ё', 'е')
    text = create_words_info_array(text)
    return ' '.join(text)


def normalize_object(item):
    if type(item) == str:
        item = normalize_text(item)

    elif type(item) == dict:
        item_copy = item.copy()
        for key in item_copy.keys():
            item_copy[key] = normalize_object(item_copy[key])
        item = item_copy

    elif type(item) == list:
        item_copy = []
        for list_item in item:
            item_copy.append(normalize_object(list_item))
        item = item_copy

    return item


def get_meilisearch_client():
    return meilisearch.Client(MEILISEARCH_ADDRESS, MEILI_MASTER_KEY)


def add_documents(documents: list, index_name, primary_key='index'):
    try:
        client = get_meilisearch_client()
        # index_name = f"{theme}_{table}"
        task = client.index(index_name).add_documents(documents, primary_key=primary_key)
    except MeiliSearchApiError as e:
        print("MeiliSearchApiError:", e)
        # raise ('Error while creating index')


def get_names_index(theme, table):
    return f"names_{theme}_{table}"


def get_full_data_index(theme, table):
    return f"full_{theme}_{table}"


def get_names_entities_index(theme):
    return f"names_{theme}"


def get_full_data_entities_index(theme):
    return f"full_{theme}"


def add_names_to_index(names: list, table, theme=HISTORY_THEME, primary_key='index'):
    index_name = get_names_index(theme, table)
    only_names = [{
        "name": item["name"],
        "normalize": normalize_text(item["name"]),
        primary_key: item[primary_key],
    } for item in names]
    # if table == "SCULPTURE":
    #     print("NAMES:", only_names[:8])
    add_documents(only_names, index_name=index_name, primary_key=primary_key)


def add_names_to_entity_index(names: list, theme=HISTORY_THEME, primary_key='id'):
    index_name = get_names_entities_index(theme)
    only_names = [{
        "name": item["name"],
        "entity": item,
        "normalize": normalize_text(item["name"]),
        primary_key: item[primary_key],
    } for item in names]
    # if table == "SCULPTURE":
    #     print("NAMES:", only_names[:8])
    add_documents(only_names, index_name=index_name, primary_key=primary_key)


def add_full_documents_to_index(documents: list, table, theme=HISTORY_THEME, primary_key='index'):
    index_name = get_full_data_index(theme, table)
    normalize_documents = [normalize_object(doc) for doc in documents]
    add_documents(normalize_documents, index_name=index_name, primary_key=primary_key)


def add_full_documents_to_entity_index(documents: list, theme=HISTORY_THEME, primary_key='id'):
    index_name = get_full_data_entities_index(theme)
    normalize_documents = [{
        'normalize': normalize_object(doc),
        "entity": doc,
        primary_key: doc[primary_key],
    } for doc in documents]
    add_documents(normalize_documents, index_name=index_name, primary_key=primary_key)


def add_name_to_index(content_item, table):
    add_names_to_index([content_item], table)


def add_name_to_entity_index(content_item):
    add_names_to_entity_index([content_item])


def add_full_document_to_index(content_item, table):
    add_full_documents_to_index([content_item], table)


def add_full_document_to_entity_index(content_item):
    add_full_documents_to_entity_index([content_item])


def delete_documents(documents, index_name):
    """

    :param documents: list of ids !!!!!!!!
    :param index_name:
    :return: None
    """
    try:
        client = get_meilisearch_client()
        task = client.index(index_name).delete_documents(documents)
    except MeiliSearchApiError as e:
        print("MeiliSearchApiError:", e)


def search(query, index_name, limit=20, offset=0, full_coincidence=False, options=None):
    try:
        client = get_meilisearch_client()
        normalize_query = normalize_text(query)
        total_options = {
            'limit': limit,
            'offset': offset
        }
        if options is not None:
            for key in options:
                total_options[key] = options[key]
        if full_coincidence:
            normalize_query = f'"{normalize_query}"'
        search_result = client.index(index_name).search(normalize_query, total_options)
        return search_result
    except MeiliSearchApiError as e:
        print("MeiliSearchApiError:", e)
    # return search_result  #.hits, search_result.processingTimeMs


def search_name(query, table, theme=HISTORY_THEME, limit=10, offset=0, options=None):
    index_name = get_names_index(theme, table)
    return search(query, index_name, limit=limit, offset=offset, options=options)


def search_entity_name(query, theme=HISTORY_THEME, limit=10, offset=0, options=None):
    index_name = get_names_entities_index(theme)
    return search(query, index_name, limit=limit, offset=offset, options=options)


def search_full_data(query, table, theme=HISTORY_THEME, limit=20, offset=0, options=None):
    index_name = get_full_data_index(theme, table)
    return search(query, index_name, limit=limit, offset=offset, options=options)


def search_full_data_entity(query, theme=HISTORY_THEME, limit=20, offset=0, options=None):
    index_name = get_full_data_entities_index(theme)
    return search(query, index_name, limit=limit, offset=offset, options=options)
