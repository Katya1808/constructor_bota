import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from asgiref.sync import sync_to_async  # ← ВАЖНО: эта обертка решает проблему!

from .models import Bot, BotUser, Scenario, Step
from .gpt_service import gpt_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramBotHandler:
    def __init__(self, bot_instance):
        self.bot_instance = bot_instance

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user

        # ⬇️ БЕЗОПАСНЫЙ асинхронный запрос к базе данных
        bot_user, created = await sync_to_async(BotUser.objects.get_or_create)(
            bot=self.bot_instance,
            external_id=str(user.id),
            defaults={'name': user.full_name or user.username}
        )

        # ⬇️ БЕЗОПАСНЫЙ асинхронный запрос к базе данных
        scenario = await sync_to_async(Scenario.objects.filter)(
            bot=self.bot_instance,
            trigger='/start',
            is_active=True
        ).afirst()  # afirst() - это асинхронная версия .first()

        if scenario:
            bot_user.current_scenario = scenario
            first_step = await sync_to_async(scenario.steps.filter)(order=1).afirst()
            bot_user.current_step = first_step
            await sync_to_async(bot_user.save)()

            if first_step:
                response = gpt_service.process_scenario_step(first_step, '')
                await update.message.reply_text(response)
            else:
                await update.message.reply_text("Привет! Я бот Alpina Digital. Чем могу помочь?")
        else:
            await update.message.reply_text("Привет! Я бот Alpina Digital. Чем могу помочь?")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик обычных сообщений"""
        user = update.effective_user
        user_message = update.message.text

        try:
            # ⬇️ БЕЗОПАСНЫЙ асинхронный запрос к базе данных
            bot_user = await sync_to_async(BotUser.objects.get)(
                bot=self.bot_instance,
                external_id=str(user.id)
            )
        except BotUser.DoesNotExist:
            await update.message.reply_text("Пожалуйста, нажмите /start для начала работы")
            return

        # Если есть текущий шаг сценария
        if bot_user.current_step:
            response = gpt_service.process_scenario_step(bot_user.current_step, user_message)
            await update.message.reply_text(response)

            # Переход к следующему шагу
            if bot_user.current_step.next_step:
                bot_user.current_step = bot_user.current_step.next_step
                await sync_to_async(bot_user.save)()
        else:
            # Если нет сценария, используем GPT напрямую
            messages = [
                {"role": "system", "content": "Ты полезный ассистент Alpina Digital."},
                {"role": "user", "content": user_message}
            ]
            response = gpt_service.chat_completion(messages)
            await update.message.reply_text(response)


def run_telegram_bot(bot_id):
    """Запуск бота Telegram"""
    try:
        # Здесь get() безопасен, так как функция run_telegram_bot НЕ является async
        bot_instance = Bot.objects.get(id=bot_id, platform='telegram')
    except Bot.DoesNotExist:
        logger.error(f"Бот с ID {bot_id} не найден или не является Telegram-ботом")
        return

    application = Application.builder().token(bot_instance.token).build()
    handler = TelegramBotHandler(bot_instance)

    application.add_handler(CommandHandler("start", handler.start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler.handle_message))

    logger.info(f"✅ Запуск бота: {bot_instance.name}")
    application.run_polling()