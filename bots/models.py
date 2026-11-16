from django.db import models
from django.contrib.auth.models import User


class Bot(models.Model):
    """Модель бота"""
    PLATFORM_CHOICES = [
        ('telegram', 'Telegram'),
        ('whatsapp', 'WhatsApp'),
        ('web', 'Web Widget'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('active', 'Активен'),
        ('paused', 'Приостановлен'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bots')
    name = models.CharField(max_length=100, verbose_name='Название бота')
    description = models.TextField(blank=True, verbose_name='Описание')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='telegram')
    token = models.CharField(max_length=255, blank=True, help_text='Токен бота')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    settings = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Бот'
        verbose_name_plural = 'Боты'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.platform})"


class Scenario(models.Model):
    """Модель сценария"""
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name='scenarios')
    name = models.CharField(max_length=100, verbose_name='Название сценария')
    description = models.TextField(blank=True)
    trigger = models.CharField(max_length=50, help_text='Триггер запуска')
    is_active = models.BooleanField(default=True)
    scenario_data = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Сценарий'
        verbose_name_plural = 'Сценарии'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (для {self.bot.name})"


class Step(models.Model):
    """Модель шага сценария"""
    STEP_TYPE_CHOICES = [
        ('message', 'Сообщение'),
        ('question', 'Вопрос'),
        ('gpt_request', 'Запрос к GPT'),
        ('action', 'Действие'),
        ('condition', 'Условие'),
    ]

    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name='steps')
    order = models.PositiveIntegerField(verbose_name='Порядок шага')
    step_type = models.CharField(max_length=20, choices=STEP_TYPE_CHOICES)
    content = models.JSONField(default=dict)
    next_step = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='previous_steps')
    conditions = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Шаг'
        verbose_name_plural = 'Шаги'
        ordering = ['order']
        unique_together = ['scenario', 'order']

    def __str__(self):
        return f"Шаг {self.order}: {self.get_step_type_display()}"


class BotUser(models.Model):
    """Модель пользователя бота"""
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name='bot_users')
    external_id = models.CharField(max_length=100)
    name = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    current_scenario = models.ForeignKey(Scenario, on_delete=models.SET_NULL, null=True, blank=True)
    current_step = models.ForeignKey(Step, on_delete=models.SET_NULL, null=True, blank=True)

    last_active = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Пользователь бота'
        verbose_name_plural = 'Пользователи ботов'
        unique_together = ['bot', 'external_id']

    def __str__(self):
        return f"{self.name} ({self.external_id})"