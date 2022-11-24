import json
from rest_framework.exceptions import ParseError

from Content.constants import TABLE, THEORY, PRACTISE, QUESTIONS, ITEMS, NAME, VIDEOS, INDEX, \
    CONST_CONTENT_TABLE_NUMBERS
from Content.models import MediaBlock, Product, TrainerBlock, VideoInformation, ContentVideo, ContentEntity, \
    ContentIndexRelationship
from Content.serializers import MediaProductSerializer, ContentWikiPreviewSerializer, ContentEntityReadOnlySerializer, \
    ContentWikiItemSerializer
from Services.service.search import add_full_document_to_index, add_name_to_index, add_name_to_entity_index, \
    add_full_document_to_entity_index
from Content.utils.wiki_content import TABLES


def update_theory_table_item(item):
    new_blocks_ids = []
    lesson_name = item[NAME].strip()
    print("|>>> Lesson name:", lesson_name)
    for block in item["blocks"]:
        media_block, _ = MediaBlock.objects.update_or_create(
            name=lesson_name + '__' + block[NAME].strip(),
            defaults={'text': block['text'].strip()})
        new_blocks_ids.append(media_block)

    product, _ = Product.objects.update_or_create(
        name=lesson_name,
        index=int(item["index"]),
        active=2,
        defaults={
            'lesson_type': 'p1',
            'theme': "",
            'section': item["section"].strip(),
            'tag': ""
        })
    product.media_blocks.set(new_blocks_ids)
    product.save()
    return product


def update_question_table_item(item):
    new_blocks_ids = []
    test_name = item[NAME].strip()
    section = item["section"].strip()
    print("|>>> Test name:", test_name)
    for question in item["questions"]:
        if "img" in question.keys():
            trainer_block, _ = TrainerBlock.objects.update_or_create(
                question=question['question'].strip(),
                answers=question['answers'].strip(),
                valid_answers=question['valid_answers'].strip(),
                active=0,
                img=question['img'],
                section=section,
                question_type=question['question_type'].strip(),
                # defaults={'question_type': question['question_type'].strip()}
            )
        else:
            trainer_block, _ = TrainerBlock.objects.update_or_create(
                question=question['question'].strip(),
                answers=question['answers'].strip(),
                valid_answers=question['valid_answers'].strip(),
                active=0,
                section=section,
                question_type=question['question_type'].strip(),
                # defaults={'question_type': question['question_type'].strip()}
            )

        new_blocks_ids.append(trainer_block)

    product, _ = Product.objects.update_or_create(
        name=test_name,
        index=int(item["index"]),
        active=2,
        defaults={
            'lesson_type': 'p2',
            'theme': "",
            'section': section,
            'tag': "ege1"
        })
    product.trainer_blocks.set(new_blocks_ids)
    product.save()
    return product


def update_or_create_entity_content(content_item, table: str, alternative_names=None, rank=1, wikidata_id=None):
    entity = content_item.entity
    index = content_item.index
    table_number = CONST_CONTENT_TABLE_NUMBERS[table]
    serializer = ContentWikiPreviewSerializer(content_item, context={"full_admin": True, "table": table})
    item_data = serializer.data

    update_dict = {}
    if wikidata_id is not None:
        update_dict.update({"wikidata_id": wikidata_id})

    if entity:
        queryset = ContentEntity.objects.filter(id=entity.id)
    else:
        queryset = ContentEntity.objects.filter(index=index, table=table_number)
    if queryset.exists():
        if alternative_names is None:
            alternative_names = queryset.first().alternative_names
        else:
            if type(alternative_names) == list:
                alternative_names = json.dumps(alternative_names)
        queryset.update(
            table=table_number,
            alternative_names=alternative_names,
            rank=rank,
            **item_data,  # description, text, index, name, optional: image
            **update_dict,  # wikidata_id
        )
        entity = queryset.first()
    else:
        if alternative_names is None:
            alternative_names = "[]"
        else:
            if type(alternative_names) == list:
                alternative_names = json.dumps(alternative_names)
        entity = ContentEntity.objects.create(
            table=table_number,
            alternative_names=alternative_names,
            rank=rank,
            **item_data,  # description, text, index, name, optional: image
            **update_dict,  # wikidata_id
        )

    return entity


def update_video_table_item(item):
    collision = None
    key = item["key"]
    name = item["name"]
    index = item["index"]
    image = item["image"]
    timestamp = item["timestamp"]

    exists_info = VideoInformation.objects.filter(key=key)
    if exists_info.exists():
        base_video = exists_info.first()
    else:
        base_video = VideoInformation.objects.create(
            name=name,
            key=key,
            image=image
        )

    exists_video = ContentVideo.objects.filter(index=index)
    if exists_video.exists():
        video = exists_video.first()
        if video.video.key == key:
            return
        else:
            collision = [key, video.video.key, index]
    else:
        video_args = {
            "index": index,
            "video": base_video,
            "time_code": timestamp,
        }
        if name != base_video.name:
            video_args["name"] = name
        if image != base_video.image:
            video_args["image"] = image
        video = ContentVideo.objects.create(
            **video_args,
            # defaults={
            #     "time_code": timestamp
            # }
        )
        print("|> Create video:", video.index)
    return collision


def content_total_update(data: list):
    """
    Total pipeline for update all entities in DB and search index.

    1. Update entity in content table (ex. in ContentPersons)
    2. Update entity in ContentEntity (get by FK from content table)
    3. Update names search indexes:
        a. Entity name search index
        b. Table name search index
    4. Update common search index (with id from entity as PK)
    :param data: dict {
        table: <content table name>,
        items: array of dict (content item for table): [{index: xxx, name: yyy, ...}, ...]
    }
    :return: None
    """

    print("|> Table:", data[TABLE])
    # FOR THEORY IN LAST COMMON BLOCK
    # if data[TABLE] == THEORY:
    #     try:
    #         for item in data[ITEMS]:
    #             product = update_theory_table_item(item)
    #             add_full_document_to_index(MediaProductSerializer(product).data, THEORY)
    #             add_name_to_index(MediaProductSerializer(product).data, THEORY)
    #     except Exception as e:
    #         print("ERROR THEORY:", e)
    #         raise ParseError(detail=f"Error during adding theory: {e}")
    #         # return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    #     # return 200

    if data[TABLE] == PRACTISE or data[TABLE] == QUESTIONS:
        # ONLY CREATE NEW QUESTIONS BECAUSE QUESTIONS DON'T HAVE INDEXES IF 'ALL WORK' TABLE
        # AND UPDATE CURRENT TESTS
        # [!] TrainerBlock.objects.update_or_create - HAS NOT BEEN TESTED
        # [!] TrainerBlock.objects.create - WORKED 100%
        for item in data[ITEMS]:
            update_question_table_item(item)

    elif data[TABLE] == VIDEOS:
        # ONLY CREATE NEW VIDEOS!
        collisions = []
        for item in data[ITEMS]:
            collision = update_video_table_item(item)
            if collision is not None:
                collisions.append(collision)
        print({"result": "ok", "collisions": collisions})
        # return {"result": "ok", "collisions": collisions}

    # MAIN CONTENT UPDATE
    else:
        content_table = TABLES[data[TABLE]]
        table_name = data[TABLE]
        is_theory = table_name == THEORY
        # Update for all content tables
        for item in data[ITEMS]:
            try:
                index = int(item[INDEX])
                if is_theory:
                    content_item = update_theory_table_item(item)
                else:
                    content_queryset = content_table.objects.filter(index=index)
                    if content_queryset.exists():
                        content_queryset.update(**item, )
                    else:
                        content_table.objects.create(**item, )
                    content_item = content_table.objects.get(index=index)

                # 2. UPDATE ENTITY RELATED TO THIS CONTENT ITEM
                entity = update_or_create_entity_content(
                    content_item,
                    table_name,
                    # TODO: ADD EXTRA KWARGS [WIKIDATA_ID, ALTERNATIVE_NAMES, RANK] FROM TABLE "ALL_WORKS"
                )
                if not is_theory:
                    content_item.entity = entity
                    content_item.save()

                # 3. UPDATE NAMES SEARCH INDEXES:
                #   A. CONTENT TABLES NAMES INDEX
                add_name_to_index(item, table_name)
                #   B. ENTITY NAMES INDEX
                entity_data = ContentEntityReadOnlySerializer(entity).data
                add_name_to_entity_index(entity_data)
                # 4. UPDATE FULL DOCUMENT INDEXES
                add_full_document_to_index(item, table_name)
                #   COMMON ENTITY INDEX
                if is_theory:
                    add_info = {'item': MediaProductSerializer(content_item).data}
                else:
                    add_info = {
                        'item': ContentWikiItemSerializer(
                            content_item, context={"access": True, "table": table_name}
                        ).data
                    }
                entity_data.update(add_info)
                add_full_document_to_entity_index(entity_data)

            except Exception as e:
                print(
                    f"|> ERROR UPDATE | table = {table_name}, index = {str(item[INDEX])} | ERROR: {str(e)}")
                continue

    return 200


def update_content_indexes_relations(data):

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
