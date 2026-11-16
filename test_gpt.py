import os
import django

# Настраиваем Django перед импортом моделей
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot_constructor.settings')
django.setup()

from bots.gpt_service import gpt_service

print("=" * 60)
print("ТЕСТ 1: Простой диалог с GPT")
print("=" * 60)

messages = [
    {"role": "system", "content": "Ты полезный ассистент Alpina Digital."},
    {"role": "user", "content": "Расскажи о компании Alpina Digital"}
]

response = gpt_service.chat_completion(messages)
print("\nОтвет GPT:")
print(response)

print("\n" + "=" * 60)
print("ТЕСТ 2: Обработка шага сценария")
print("=" * 60)

from bots.models import Scenario, Step

scenario = Scenario.objects.first()
if scenario:
    print(f"Найден сценарий: {scenario.name}")
    step = scenario.steps.filter(step_type='gpt_request').first()
    if step:
        print(f"Найден шаг типа gpt_request: {step}")
        response = gpt_service.process_scenario_step(step, "Привет, как дела?")
        print("\nОтвет на шаге:")
        print(response)
    else:
        print("⚠️ Нет шага типа gpt_request в этом сценарии")
        print("Создайте шаг через админку или API")
else:
    print("⚠️ Нет сценариев в базе данных")
    print("Создайте сценарий через админку или API")

print("\n" + "=" * 60)
print("Тестирование завершено!")
print("=" * 60)