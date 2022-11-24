from django.contrib import admin
from Statistics.models import ProductLog, ProductProgress, TrainerBlockProgress, TrainerBlockLog, ActivityLog, \
    GenerateLog, AnswersProgressState, UserAnswerForReview
from Statistics.models import InitLog, MetricsCache, WeekRating, Achievement, UserMetric
from Users.admin import StaffRequiredAdminMixin


@admin.register(Achievement)
class AchievementAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'category', 'value')
    readonly_fields = ('id',)


@admin.register(UserMetric)
class UserMetricAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'metric', 'value')
    search_fields = ('user__username', 'metric', 'id')
    readonly_fields = ('id',)
    raw_id_fields = ('user',)


@admin.register(ActivityLog)
class ActivityLogAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'activity', 'timestamp')
    readonly_fields = ('user', 'activity', 'timestamp')
    raw_id_fields = ('user',)


@admin.register(ProductLog)
class ProductLogAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'product', 'completed', 'time_to_complete')
    readonly_fields = ('id',)
    raw_id_fields = ('user',)


@admin.register(ProductProgress)
class ProductProgressAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ('product', 'user', 'completed', )
    search_fields = ('product__name', 'user__username', )
    raw_id_fields = ('user',)


@admin.register(TrainerBlockProgress)
class TrainerBlockProgressAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'trainer_block', 'balance', 'attempts', 'successful_attempts')
    search_fields = ('user__username', 'trainer_block__question', )
    readonly_fields = ('user', 'balance', )
    raw_id_fields = ('user',)


@admin.register(TrainerBlockLog)
class TrainerBlockLogAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'is_valid', 'answer')
    raw_id_fields = ('user',)


@admin.register(GenerateLog)
class GenerateLogAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'text', 'amount', 'timestamp')
    raw_id_fields = ('user',)


@admin.register(InitLog)
class InitLogAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'title', 'timestamp', 'version')
    search_fields = ('user__username', )
    raw_id_fields = ('user',)


@admin.register(MetricsCache)
class CashLogAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ('value', 'day', 'average', 'metric')
    search_fields = ('metric', 'day')


@admin.register(WeekRating)
class WeekRatingAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'value', 'status', 'best_place')
    raw_id_fields = ('user',)


@admin.register(AnswersProgressState)
class AnswersProgressStateAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'date', 'top_percent', 'right_answers_per_day')
    raw_id_fields = ('user',)


@admin.register(UserAnswerForReview)
class UserAnswerForReviewAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'problem', 'status', 'answer')
    raw_id_fields = ('user',)


# @admin.register(CashLogTime)
# class CashLogTimeAdmin(admin.ModelAdmin):
#     list_display = ('count', 'day', 'metric')
