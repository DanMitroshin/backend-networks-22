from Users.models import User, UserAchievementRelation, NotificationPushToken, \
    BannedUser, UserInfoVersion

from funcy import first, walk
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


class StaffRequiredAdminMixin(object):

    def check_perm(self, user_obj, action=None):
        if not user_obj.is_active or user_obj.is_anonymous:
            return False
        if user_obj.is_superuser or (user_obj.is_staff and action in ["view", "module"]):
            return True
        return False

    def has_add_permission(self, request):
        return self.check_perm(request.user, "add")

    def has_change_permission(self, request, obj=None):
        return self.check_perm(request.user, "change")

    def has_delete_permission(self, request, obj=None):
        return self.check_perm(request.user, "delete")

    def has_module_permission(self, request, obj=None):
        return self.check_perm(request.user, "module")

    def has_view_permission(self, request, obj=None):
        return self.check_perm(request.user, "view")


class AccessGroupsInline(admin.TabularInline):
    model = User.access_groups.through


class AchievementsInline(admin.TabularInline):
    model = User.achievements.through


# Register out own model admin, based on the default UserAdmin
@admin.register(User)
class CustomUserAdmin(StaffRequiredAdminMixin, UserAdmin):
    inlines = (AccessGroupsInline, AchievementsInline,)

    def get_form(self, request, obj=None, **kwargs):
        kwargs['widgets'] = {
            'nickname': forms.TextInput(attrs={'placeholder': "" if obj is None else obj.get_nickname()})
        }
        return super().get_form(request, obj, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Searching and filtering
        self.search_fields += ('vk_id', 'nickname', 'identifier', 'id')
        self.list_filter += ('is_teacher', )
        self.list_display += ('nickname', 'vk_id', )  # don't forget the commas
        self.readonly_fields += (
            # 'identifier',
            'account_token',
            'id',
        )

        # Editing
        def extend_fieldset(fieldset):
            name, options = fieldset
            if name == 'Permissions':
                fields = list(options['fields'])
                fields.insert(3, 'is_teacher')
                options['fields'] = tuple(fields)
            if name == 'Personal info':
                options['fields'] += (
                    'id',
                    'vk_id',
                    'vk_access_token',
                    'identifier',
                    'account_token',
                    'version_app',
                    'nickname',
                    'device',
                    'registration_platform',
                )
            if name == 'Important dates':
                options['fields'] += ('last_entry', )
            return name, options

        self.fieldsets = walk(extend_fieldset, self.fieldsets)

        ###########
        new_fieldsets = list(self.fieldsets)
        new_fieldsets.insert(2, ("Additional info", {
            'fields': (
                'sex',
                'image',
                'image_50',
                'coins',
                'rating_stars',
                'country',
                'city',
                'educational_institution',
                'date_of_birth',
            )})
        )
        self.fieldsets = tuple(new_fieldsets)


@admin.register(BannedUser)
class BannedUserAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'type', 'end_day')
    search_fields = ('user__username',)
    autocomplete_fields = ('user', )


@admin.register(UserAchievementRelation)
class UserAchievementRelationAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'achieve')
    raw_id_fields = ('user',)


@admin.register(NotificationPushToken)
class NotificationPushTokenAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'token', 'type', 'active')
    search_fields = ('user__username', 'token')
    raw_id_fields = ('user',)


@admin.register(UserInfoVersion)
class UserInfoVersionAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'app_version', 'dialog_version', 'last_dialog_time', 'notification_version')
    search_fields = ('user__username', )
    raw_id_fields = ('user',)

