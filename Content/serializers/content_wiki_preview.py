from rest_framework import serializers
from Content.constants import CLASS_CONTENT_TABLE_ACCESS_INDEX_LIMITS, \
    CLASS_CONTENT_TABLE_NAMES, CREATE_PREVIEW_FUNCTIONS, CREATE_PREVIEW_DESCRIPTION_FUNCTIONS
from Content.models import ContentPerson, ContentTerm, ContentEvent, ContentArchitecture, ContentPicture, \
    ContentSculpture, ContentLiterature, ContentMap


class ContentPreviewTemplateSerializer(serializers.ModelSerializer):
    TABLE = None
    ACCESS_INDEX = None
    ITEMS_NAME = None  # Use this if you want to get this name for all items

    # @staticmethod
    def preview_function(self, info):
        return CREATE_PREVIEW_FUNCTIONS[self.TABLE](info)

    def preview_description_function(self, info):
        return CREATE_PREVIEW_DESCRIPTION_FUNCTIONS[self.TABLE](info)

    def to_representation(self, instance):

        # ADMIN REPRESENTATION FOR ENTITY TABLE
        if self.context.get("full_admin", False):
            serializer = super().to_representation(instance)
            serializer = self.create_full_admin_representation(serializer)
            return serializer
        access = self.context.get("access", False) or instance.index < self.ACCESS_INDEX or self.ACCESS_INDEX < 0
        serializer = super().to_representation(instance)
        if not access:
            serializer = self.create_hidden_representation(serializer)
        else:
            serializer = self.create_open_representation(serializer)
        # except Exception as e:
        #     print("Err", e)

        return serializer

    def create_full_admin_representation(self, representation):
        new_representation = {
            "name": self.ITEMS_NAME if self.ITEMS_NAME else representation["name"],
            "index": representation["index"],
            "text": self.preview_function(representation),
            "description": self.preview_description_function(representation),
        }
        if representation.get("image", False):
            if representation.get("image_100", False):
                new_representation.update({
                    "image": representation["image_100"],
                    "full_image": representation["image"],
                })
            else:
                new_representation.update({"image": representation["image"]})
        return new_representation

    def create_base_representation(self, representation):
        return {
            "name": self.ITEMS_NAME if self.ITEMS_NAME else representation["name"],
            "index": representation["index"],
            "table": self.TABLE,
        }

    def create_open_representation(self, representation: dict):
        new_representation = self.create_base_representation(representation)
        new_representation.update({
            "hidden": False,
        })

        if representation.get("image", False):
            if representation.get("image_100", False):
                new_representation.update({
                    "image": representation["image_100"],
                    "full_image": representation["image"],
                })
            else:
                new_representation.update({"image": representation["image"]})

        new_representation.update({"text": self.preview_function(representation)})

        return new_representation

    def create_hidden_representation(self, representation: dict):
        new_representation = self.create_base_representation(representation)
        new_representation.update({
            "hidden": True,
        })

        if representation.get("image", False):
            new_representation.update({"image": True})

        return new_representation


class ContentPersonPreviewSerializer(ContentPreviewTemplateSerializer):
    ACCESS_INDEX = CLASS_CONTENT_TABLE_ACCESS_INDEX_LIMITS.PERSONS
    TABLE = CLASS_CONTENT_TABLE_NAMES.PERSONS

    class Meta:
        model = ContentPerson
        fields = ['index', 'name', 'image', 'image_100', 'summary']
        read_only = True


class ContentTermPreviewSerializer(ContentPreviewTemplateSerializer):
    ACCESS_INDEX = CLASS_CONTENT_TABLE_ACCESS_INDEX_LIMITS.TERMS
    TABLE = CLASS_CONTENT_TABLE_NAMES.TERMS

    class Meta:
        model = ContentTerm
        fields = ['index', 'name', 'definition']
        read_only = True


class ContentEventPreviewSerializer(ContentPreviewTemplateSerializer):
    ACCESS_INDEX = CLASS_CONTENT_TABLE_ACCESS_INDEX_LIMITS.DATES_RUS
    TABLE = CLASS_CONTENT_TABLE_NAMES.DATES_RUS

    class Meta:
        model = ContentEvent
        fields = ['index', 'name', 'date']
        read_only = True


class ContentArchitecturePreviewSerializer(ContentPreviewTemplateSerializer):
    ACCESS_INDEX = CLASS_CONTENT_TABLE_ACCESS_INDEX_LIMITS.ARCHITECTURE
    TABLE = CLASS_CONTENT_TABLE_NAMES.ARCHITECTURE

    class Meta:
        model = ContentArchitecture
        fields = ['index', 'image', 'image_100', 'name', 'architect']
        read_only = True


class ContentPicturePreviewSerializer(ContentPreviewTemplateSerializer):
    ACCESS_INDEX = CLASS_CONTENT_TABLE_ACCESS_INDEX_LIMITS.PICTURES
    TABLE = CLASS_CONTENT_TABLE_NAMES.PICTURES

    class Meta:
        model = ContentPicture
        fields = ['index', 'image', 'image_100', 'name', 'author']
        read_only = True


class ContentSculpturePreviewSerializer(ContentPreviewTemplateSerializer):
    ACCESS_INDEX = CLASS_CONTENT_TABLE_ACCESS_INDEX_LIMITS.SCULPTURE
    TABLE = CLASS_CONTENT_TABLE_NAMES.SCULPTURE

    class Meta:
        model = ContentSculpture
        fields = ['index', 'image', 'image_100', 'name', 'author']
        read_only = True


class ContentLiteraturePreviewSerializer(ContentPreviewTemplateSerializer):
    ACCESS_INDEX = CLASS_CONTENT_TABLE_ACCESS_INDEX_LIMITS.LITERATURE
    TABLE = CLASS_CONTENT_TABLE_NAMES.LITERATURE

    class Meta:
        model = ContentLiterature
        fields = ['index', 'image', 'image_100', 'name', 'author']
        read_only = True


class ContentMapPreviewSerializer(ContentPreviewTemplateSerializer):
    ACCESS_INDEX = CLASS_CONTENT_TABLE_ACCESS_INDEX_LIMITS.MAPS
    TABLE = CLASS_CONTENT_TABLE_NAMES.MAPS

    class Meta:
        model = ContentMap
        fields = ['index', 'image', 'image_100', 'name']
        read_only = True
