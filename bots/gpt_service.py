from openai import OpenAI
from django.conf import settings
import time


class GPTService:
    """Универсальный сервис для работы с LLM (поддерживает OpenAI, Qwen, DeepSeek и др.)"""

    def __init__(self):
        # Если ключа нет, включаем режим имитации
        self.use_mock = not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == 'sk-your-api-key-here'

        if not self.use_mock:
            # Инициализируем клиент с возможностью переопределения базового URL
            self.client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=getattr(settings, 'OPENAI_BASE_URL', 'https://api.openai.com/v1')
            )

        self.model = getattr(settings, 'OPENAI_MODEL', 'qwen/qwen-2.5-72b-instruct')

    def chat_completion(self, messages, temperature=0.7, max_tokens=500):
        """Отправка запроса к LLM"""

        if self.use_mock:
            print("⚠️ [MOCK] Имитация ответа (нет API ключа)")
            time.sleep(1)
            return "[Имитация]: Alpina Digital — это цифровая экосистема корпоративного обучения..."

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Ошибка LLM API: {str(e)}"

    def process_scenario_step(self, step, user_message):
        """Обработка шага сценария"""
        if step.step_type == 'gpt_request':
            content = step.content or {}
            prompt_template = content.get('prompt', '{user_input}')
            system_message = content.get('system_message', 'Ты полезный ассистент Alpina Digital.')

            prompt = prompt_template.replace('{user_input}', user_message)

            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]

            return self.chat_completion(messages)

        elif step.step_type == 'message':
            content = step.content or {}
            return content.get('text', 'Сообщение без текста')

        return None


gpt_service = GPTService()