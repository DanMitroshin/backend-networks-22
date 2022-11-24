from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from Content.constants import CREATE_FULL_CONTENT_FUNCTIONS
from Content.constants import CLASS_CONTENT_TABLE_ACCESS_INDEX_LIMITS, CLASS_CONTENT_TABLE_NAMES
from Content.models import ContentPerson, ContentTerm, ContentEvent, ContentArchitecture, ContentPicture, \
    ContentSculpture, ContentLiterature, ContentMap, ContentVideo
from Content.utils.wiki_content import LIST_WIKI_TABLES


class ContentWikiItemTemplateSerializer(serializers.ModelSerializer):
    TABLE = None
    ACCESS_INDEX = None

    def to_representation(self, instance):
        access = self.context.get("access", False) or instance.index < self.ACCESS_INDEX or self.ACCESS_INDEX < 0

        if not access:
            raise PermissionDenied(detail="[content] No permissions to view")
        serializer = super().to_representation(instance)
        item_data = CREATE_FULL_CONTENT_FUNCTIONS[self.TABLE](serializer)
        item_data.update({
            "index": instance.index,
            "table": self.TABLE,
        })

        return item_data


class ContentPersonItemSerializer(ContentWikiItemTemplateSerializer):
    ACCESS_INDEX = CLASS_CONTENT_TABLE_ACCESS_INDEX_LIMITS.PERSONS
    TABLE = CLASS_CONTENT_TABLE_NAMES.PERSONS

    class Meta:
        model = ContentPerson
        exclude = ('entity', )
        # fields = '__all__'
        read_only = True


class ContentTermItemSerializer(ContentWikiItemTemplateSerializer):
    ACCESS_INDEX = CLASS_CONTENT_TABLE_ACCESS_INDEX_LIMITS.TERMS
    TABLE = CLASS_CONTENT_TABLE_NAMES.TERMS

    class Meta:
        model = ContentTerm
        exclude = ('entity', )
        # fields = '__all__'
        read_only = True


class ContentEventItemSerializer(ContentWikiItemTemplateSerializer):
    ACCESS_INDEX = CLASS_CONTENT_TABLE_ACCESS_INDEX_LIMITS.DATES_RUS
    TABLE = CLASS_CONTENT_TABLE_NAMES.DATES_RUS

    class Meta:
        model = ContentEvent
        exclude = ('entity', )
        # fields = '__all__'
        read_only = True


class ContentArchitectureItemSerializer(ContentWikiItemTemplateSerializer):
    ACCESS_INDEX = CLASS_CONTENT_TABLE_ACCESS_INDEX_LIMITS.ARCHITECTURE
    TABLE = CLASS_CONTENT_TABLE_NAMES.ARCHITECTURE

    class Meta:
        model = ContentArchitecture
        exclude = ('entity', )
        # fields = '__all__'
        read_only = True


class ContentPictureItemSerializer(ContentWikiItemTemplateSerializer):
    ACCESS_INDEX = CLASS_CONTENT_TABLE_ACCESS_INDEX_LIMITS.PICTURES
    TABLE = CLASS_CONTENT_TABLE_NAMES.PICTURES

    class Meta:
        model = ContentPicture
        exclude = ('entity', )
        # fields = '__all__'
        read_only = True


class ContentVideoItemSerializer(ContentWikiItemTemplateSerializer):
    ACCESS_INDEX = CLASS_CONTENT_TABLE_ACCESS_INDEX_LIMITS.VIDEOS
    TABLE = CLASS_CONTENT_TABLE_NAMES.VIDEOS

    class Meta:
        model = ContentVideo
        exclude = ('entity', )
        # fields = '__all__'
        read_only = True


class ContentSculptureItemSerializer(ContentWikiItemTemplateSerializer):
    ACCESS_INDEX = CLASS_CONTENT_TABLE_ACCESS_INDEX_LIMITS.SCULPTURE
    TABLE = CLASS_CONTENT_TABLE_NAMES.SCULPTURE

    class Meta:
        model = ContentSculpture
        exclude = ('entity', )
        # fields = '__all__'
        read_only = True


class ContentLiteratureItemSerializer(ContentWikiItemTemplateSerializer):
    ACCESS_INDEX = CLASS_CONTENT_TABLE_ACCESS_INDEX_LIMITS.LITERATURE
    TABLE = CLASS_CONTENT_TABLE_NAMES.LITERATURE

    class Meta:
        model = ContentLiterature
        exclude = ('entity', )
        # fields = '__all__'
        read_only = True


class ContentMapItemSerializer(ContentWikiItemTemplateSerializer):
    ACCESS_INDEX = CLASS_CONTENT_TABLE_ACCESS_INDEX_LIMITS.MAPS
    TABLE = CLASS_CONTENT_TABLE_NAMES.MAPS

    class Meta:
        model = ContentMap
        exclude = ('entity', )
        # fields = '__all__'
        read_only = True


CONTENT_WIKI_ITEM_SERIALIZERS = {
    CLASS_CONTENT_TABLE_NAMES.PERSONS: ContentPersonItemSerializer,
    CLASS_CONTENT_TABLE_NAMES.DATES_RUS: ContentEventItemSerializer,
    CLASS_CONTENT_TABLE_NAMES.TERMS: ContentTermItemSerializer,
    CLASS_CONTENT_TABLE_NAMES.MAPS: ContentMapItemSerializer,
    CLASS_CONTENT_TABLE_NAMES.ARCHITECTURE: ContentArchitectureItemSerializer,
    CLASS_CONTENT_TABLE_NAMES.LITERATURE: ContentLiteratureItemSerializer,
    CLASS_CONTENT_TABLE_NAMES.SCULPTURE: ContentSculptureItemSerializer,
    CLASS_CONTENT_TABLE_NAMES.PICTURES: ContentPictureItemSerializer,
    CLASS_CONTENT_TABLE_NAMES.VIDEOS: ContentVideoItemSerializer,
}


class ContentWikiItemSerializer(serializers.Serializer):

    def to_representation(self, instance):
        table = self.context.get("table")
        assert table in LIST_WIKI_TABLES.keys(), 'Table not in table list'

        serializer = CONTENT_WIKI_ITEM_SERIALIZERS[table](instance, context=self.context)
        return serializer.data
