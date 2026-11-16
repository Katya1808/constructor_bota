import os
import django

# Настраиваем Django перед импортом
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot_constructor.settings')
django.setup()

from bots.telegram_bot import run_telegram_bot

# ⚠️ ВАЖНО: замените 1 на ID вашего бота из админки!
# Узнать ID можно в URL при редактировании бота:
# http://127.0.0.1:8000/admin/bots/bot/1/change/
#                                                ^ это ID

run_telegram_bot(bot_id=8)