"""
Клиент для Qwen через OpenAI-совместимый API (DashScope).
Поддерживает: qwen-plus, qwen-max, qwen-turbo, qwen-long
"""
import os
import logging
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "YOUR_DASHSCOPE_API_KEY")
QWEN_MODEL        = os.getenv("QWEN_MODEL", "qwen-plus")   # qwen-max / qwen-turbo / qwen-long


class QwenClient:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=DASHSCOPE_API_KEY,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.model = QWEN_MODEL

    async def chat(
        self,
        user_message: str,
        history: list[dict],
        system_prompt: str = "",
    ) -> str:
        """
        Отправляет сообщение с историей и возвращает ответ модели.

        history — список {"role": "user"/"assistant", "content": "..."}
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(history[-20:])          # последние 20 сообщений контекста
        messages.append({"role": "user", "content": user_message})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=2048,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Qwen API error: {e}")
            return f"⚠️ Ошибка AI: {e}\n\nПроверь API-ключ DashScope."
