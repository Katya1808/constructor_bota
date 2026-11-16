from django.contrib import admin
from .models import Bot, Scenario, Step, BotUser


class StepInline(admin.TabularInline):
    """Встроенное редактирование шагов в сценарии"""
    model = Step
    extra = 1
    fields = ['order', 'step_type', 'content', 'next_step']


class ScenarioInline(admin.TabularInline):
    """Встроенное редактирование сценариев в боте"""
    model = Scenario
    extra = 1
    fields = ['name', 'trigger', 'is_active']


@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    list_display = ['name', 'platform', 'status', 'owner', 'created_at']
    list_filter = ['platform', 'status']
    search_fields = ['name', 'description']
    inlines = [ScenarioInline]

    fieldsets = (
        (None, {
            'fields': ('owner', 'name', 'description', 'platform', 'status')
        }),
        ('Настройки', {
            'fields': ('token', 'settings'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = ['name', 'bot', 'trigger', 'is_active', 'created_at']
    list_filter = ['is_active', 'bot']
    search_fields = ['name', 'description']
    inlines = [StepInline]

    fieldsets = (
        (None, {
            'fields': ('bot', 'name', 'description', 'trigger', 'is_active')
        }),
        ('Данные сценария', {
            'fields': ('scenario_data',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    list_display = ['scenario', 'order', 'step_type', 'next_step']
    list_filter = ['step_type', 'scenario']
    search_fields = ['content']


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ['name', 'bot', 'external_id', 'last_active']
    list_filter = ['bot']
    search_fields = ['name', 'external_id']