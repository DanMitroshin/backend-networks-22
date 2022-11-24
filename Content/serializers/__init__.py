import json

from Content.serializers.content_wiki_preview import (
    ContentPersonPreviewSerializer, ContentEventPreviewSerializer, ContentMapPreviewSerializer,
    ContentSculpturePreviewSerializer, ContentArchitecturePreviewSerializer, ContentPicturePreviewSerializer,
    ContentLiteraturePreviewSerializer, ContentTermPreviewSerializer,
    ContentPreviewTemplateSerializer
)
from Content.utils.wiki_content import check_table_in_wiki_tables

from .product import (
    TrainerBlockSerializer,
    TrainerBlocksPostSerializer,
    MediaProductSerializer,
    MediaBlockSerializer,
    MediaProductPostSerializer,
    ProductListGetSerializer,
    TrainerProductCreateRetrieveSerializer,
    TrainerProductPostSerializer,
    TrainerProductSerializer,
    CheckerTrainerBlockSerializer,
    ProductLogCreateSerializer,
    TrainerBlockLogCreateSerializer,
)
from .answers import TrainerBlockCheckAnswerSerializer
from rest_framework import serializers

from Content.constants import CLASS_CONTENT_TABLE_NAMES, \
    CLASS_CONTENT_TABLE_ACCESS_INDEX_LIMITS

from .content_wiki_item import (
    CONTENT_WIKI_ITEM_SERIALIZERS, ContentWikiItemSerializer
)
from Content.models import (
    Associate,
    AccessGroup,
    ContentEntity)
from .classroom import (
    ClassroomActionSerializer,
    ClassroomCreateSerializer,
    ClassroomEnrollSerializer,
    ClassroomSerializer,
    ClassroomUpdateSerializer,
)
from .review import UserAnswerForReviewCreateSerializer
from .search import (
    NamesSearchSerializer,
)


class AccessGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessGroup
        fields = '__all__'


class AssociateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Associate
        fields = '__all__'


class ContentTheoryPreviewSerializer(ContentPreviewTemplateSerializer, MediaProductSerializer):
    ACCESS_INDEX = CLASS_CONTENT_TABLE_ACCESS_INDEX_LIMITS.THEORY
    TABLE = CLASS_CONTENT_TABLE_NAMES.THEORY

    def to_representation(self, instance):
        serializer = super().to_representation(instance)
        serializer['id'] = instance.id
        return serializer


class ContentQuestionPreviewSerializer(ContentPreviewTemplateSerializer, TrainerBlockSerializer):
    ACCESS_INDEX = CLASS_CONTENT_TABLE_ACCESS_INDEX_LIMITS.QUESTIONS
    TABLE = CLASS_CONTENT_TABLE_NAMES.QUESTIONS
    ITEMS_NAME = "Вопрос"


CONTENT_WIKI_PREVIEW_SERIALIZERS = {
    CLASS_CONTENT_TABLE_NAMES.PERSONS: ContentPersonPreviewSerializer,
    CLASS_CONTENT_TABLE_NAMES.DATES_RUS: ContentEventPreviewSerializer,
    CLASS_CONTENT_TABLE_NAMES.TERMS: ContentTermPreviewSerializer,
    CLASS_CONTENT_TABLE_NAMES.MAPS: ContentMapPreviewSerializer,
    CLASS_CONTENT_TABLE_NAMES.ARCHITECTURE: ContentArchitecturePreviewSerializer,
    CLASS_CONTENT_TABLE_NAMES.LITERATURE: ContentLiteraturePreviewSerializer,
    CLASS_CONTENT_TABLE_NAMES.SCULPTURE: ContentSculpturePreviewSerializer,
    CLASS_CONTENT_TABLE_NAMES.PICTURES: ContentPicturePreviewSerializer,
    CLASS_CONTENT_TABLE_NAMES.THEORY: ContentTheoryPreviewSerializer,
    CLASS_CONTENT_TABLE_NAMES.QUESTIONS: ContentQuestionPreviewSerializer,
}


class ContentWikiPreviewSerializer(serializers.Serializer):

    def to_representation(self, instance):
        table = self.context.get("table")
        check_table_in_wiki_tables(table)
        # print("Check table context serializer:", table)

        serializer = CONTENT_WIKI_PREVIEW_SERIALIZERS[table](instance, context=self.context)
        # print("Ser inst", instance)
        # print("Ser data", serializer.data)
        return serializer.data


class ContentEntityReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentEntity
        fields = '__all__'
        read_only = True

    def to_representation(self, instance):
        serializer = super().to_representation(instance)
        if not instance.alternative_names:
            serializer["alternative_names"] = []
        else:
            serializer["alternative_names"] = json.loads(serializer["alternative_names"])
        return serializer
