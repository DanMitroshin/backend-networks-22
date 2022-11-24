from django.contrib import admin

from Users.admin import StaffRequiredAdminMixin
from .models import (
    DuelUserState, ActiveDuel, CompletedDuel,
    DuelsConfiguration, DuelTrainerBlockRelation)


@admin.register(DuelUserState)
class DuelUserStateAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'rating_changes')
    search_fields = ('user',)
    raw_id_fields = ('user',)


@admin.register(ActiveDuel)
class ActiveDuelAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ('timestamp_create', 'creator', 'opponent')
    raw_id_fields = ('creator', 'opponent')
    # search_fields = ('name', 'id', 'text')


@admin.register(CompletedDuel)
class CompletedDuelAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ('timestamp_create', 'creator', 'opponent')
    raw_id_fields = ('creator', 'opponent')


@admin.register(DuelsConfiguration)
class DuelsConfigurationAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ('status', 'description')


@admin.register(DuelTrainerBlockRelation)
class DuelTrainerBlockRelationAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ('active_duel', 'trainer_block')
