from django.contrib import admin
from .models import Quote, Source, Vote


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'source',
        'weight',
        'views',
        'likes',
        'dislikes',
        'is_active',
        'created_at'
    )
    list_filter = ('is_active', 'source__kind')
    search_fields = ('text', 'source__name')
    list_editable = ('weight', 'is_active')
    ordering = ('-created_at',)
    actions = ['approve_quotes']

    @admin.action(description='Одобрить выбранные цитаты')
    def approve_quotes(self, request, queryset):
        """
        Массовое действие для одобрения цитат.
        """
        queryset.update(is_active=True)

@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'kind')
    search_fields = ('name',)
    list_filter = ('kind',)

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('quote', 'session_key', 'value', 'created_at')
    list_filter = ('value',)