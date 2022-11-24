from django.contrib import admin

from Content.models import ContentHistoryText
from Users.admin import StaffRequiredAdminMixin
from .utils import generate_invite_code
from .models import AccessGroup, Associate
from .models import (
    MediaBlock,
    Product,
    ContentTheme,
    TrainerBlock,
    TrainerBlockTag,
    TrainerBlockPeriod,
    TrainerBlockPerson,
    ContentTerm, ContentSculpture, ContentPicture, ContentPerson, ContentMap, ContentLiterature,
    ContentIndexRelationship, ContentArchitecture, ContentEvent, ContentVideo, VideoInformation,
    ContentDialogAnswer, ContentDialog, SpecialQuestionAnswer, ContentEntity,
)


@admin.register(Product)
class ProductAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    # Searching and filtering
    search_fields = ('name', 'id', 'index')
    list_display = ('name', 'id', 'creation_date', 'index')
    list_filter = ('lesson_type',)

    # Editing
    readonly_fields = ('id',)
    filter_horizontal = ('trainer_blocks', 'media_blocks')

    def get_fieldsets(self, request, obj=None):
        structure = {}
        fields = ('media_blocks', 'trainer_blocks')
        if obj:

            # Leave only correct blocks
            if obj.lesson_type in ('p1',):
                fields = ('media_blocks',)
            elif obj.lesson_type in ('p2', 'p3'):
                fields = ('trainer_blocks',)

        structure['fields'] = fields

        return (
            ('information', {'fields': ('name', 'theme', 'section', 'tag', 'content_theme')}),
            ('Meta', {'fields': ('lesson_type', 'active', 'id', 'index')}),
            ('Structure', structure),
            ('Access', {'fields': ('access_groups',)}),
        )

    def get_form(self, request, obj=None, **kwargs):
        exclude = ('media_blocks', 'trainer_blocks')
        if obj:

            # Leave only correct blocks
            if obj.lesson_type in ('p1',):
                exclude = 'trainer_blocks'
            elif obj.lesson_type in ('p2', 'p3'):
                exclude = 'media_blocks'

            kwargs.update({
                'exclude': getattr(kwargs, 'exclude', tuple()) + (exclude,)
            })
        return super(ProductAdmin, self).get_form(request, obj, **kwargs)


@admin.register(ContentTheme)
class ContentThemeAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'video', 'index')
    search_fields = ('name', 'index')


@admin.register(ContentEntity)
class ContentThemeAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ('wikidata_id', 'name', 'table', 'index')
    search_fields = ('name', 'index')
    list_filter = ('table',)


@admin.register(MediaBlock)
class MediaBlockAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'id')
    search_fields = ('name', 'id', 'text')


@admin.register(Associate)
class AssociateAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    search_fields = ('user',)
    list_display = ('user', 'date', 'associate',)
    raw_id_fields = ('user',)


@admin.register(TrainerBlock)
class TrainerBlockAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    # Searching and filtering
    search_fields = ('question', 'id', 'index')
    list_display = ('question', 'id', 'index', 'question_type', 'theme', 'section', 'active')
    list_filter = ('active', 'question_type', 'tags')

    # Editing
    fieldsets = (
        ('Displayed information', {'fields': ('question', 'trivia', 'img')}),
        ('Answers', {'fields': ('answers', 'valid_answers')}),
        ('Meta', {'fields': ('question_type', 'active')}),
        ('Taxonomy', {'fields': ('theme', 'section')}),
        ('Tags', {'fields': ('persons', 'periods', 'tags')}),
    )


@admin.register(TrainerBlockTag)
class TrainerBlockMetaAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    pass


@admin.register(TrainerBlockPerson)
class TrainerBlockPersonAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ("name", "person")


@admin.register(TrainerBlockPeriod)
class TrainerBlockPersonAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ("name", "period")


@admin.register(AccessGroup)
class AccessGroupAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    # Searching and filterign
    list_filter = ('type',)
    list_display = ('name', 'type')

    # Editing
    fieldsets = (
        ('Information', {'fields': ('name', 'type')}),
        ('Access', {'fields': ('invite_code',)})
    )

    def save_model(self, request, obj, form, change):
        if not obj.invite_code:
            obj.invite_code = generate_invite_code()
        super().save_model(request, obj, form, change)


@admin.register(ContentEvent)
class ContentEventAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ("name", "index", "date")


@admin.register(ContentTerm)
class ContentTermAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ("name", "index")


@admin.register(ContentPerson)
class ContentPersonAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ("name", "index", "dates_of_life")


@admin.register(ContentMap)
class ContentMapAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ("name", "index", "date")


@admin.register(ContentHistoryText)
class ContentHistoryTextAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ("name", "index", "date")


@admin.register(ContentArchitecture)
class ContentArchitectureAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ("name", "index", "date")


@admin.register(ContentPicture)
class ContentPictureAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ("name", "index", "date")


@admin.register(ContentSculpture)
class ContentSculptureAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ("name", "index", "date", "author")


@admin.register(ContentLiterature)
class ContentLiteratureAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ("name", "index", "date", "author")


@admin.register(VideoInformation)
class VideoInformationAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ("name", "key")


@admin.register(ContentVideo)
class ContentVideoAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ("video", "name", "index", "time_code")


@admin.register(ContentIndexRelationship)
class ContentLiteratureAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ("first_index", "first_code", "second_index", "second_code")
    search_fields = ("first_index", "first_code", "second_index", "second_code")


@admin.register(ContentDialog)
class ContentDialogAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ("index", "person_name", "category", "status", "save_status",)
    search_fields = ("index", "person_name", "content", "author")
    readonly_fields = ("impressions_amount", "good_actions_with_dialog_info", "bad_actions_with_dialog_info")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fieldsets = (
            (
                "Параметры отображения диалога", {
                    'fields': (
                        'index',
                        'person_name',
                        'image',
                        'content',
                    )
                }
            ),
            (
                "Настройки диалога", {
                    'fields': (
                        'status',
                        'save_status',
                        'category',
                        'app_version',
                        'author',
                    )
                }
            ),
            (
                "Статистика", {
                    'fields': (
                        "impressions_amount",
                        "good_actions_with_dialog_info",
                        "bad_actions_with_dialog_info"
                    )})
        )


@admin.register(ContentDialogAnswer)
class ContentDialogAnswerAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ("user", "dialog_index", "action_index", "timestamp")
    raw_id_fields = ('user',)


@admin.register(SpecialQuestionAnswer)
class SpecialQuestionAnswerAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ("user", "question", "timestamp")
    raw_id_fields = ('user',)
