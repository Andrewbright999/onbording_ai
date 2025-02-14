import time
from openai import AsyncOpenAI
from config import OPENAI_API_KEY

# Создаём асинхронного клиента (рекомендуется создавать экземпляр клиента, а не использовать глобальный модуль)
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# chat_completion = await client.chat.completions.create(model="gpt-4o",
#                                                                 messages=messages,
#                                                                    temperature =  0.5)
#     try:
#         response = chat_completion.choices[0].message.content
#         return response

async def validate_name(name: str) -> bool:
    """
    They send you a name, if it's a name, then write "yes", if it's not a name, then send "no".
    """
    prompt = (
        f""""if it's that word: {name} is name, then write "yes", if it's not a name, then send "no" """
    )
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": """hey send you a name, if it's a name, then write "yes", if it's not a name, then send "no"."""},
            {"role": "user", "content": prompt},
        ],
    )
    # Получаем ответ из pydantic-модели
    answer = response.choices[0].message.content.lower()
    print(answer)
    return "yes" in answer

async def analyze_feedback(feedback: str) -> str:
    """
    Анализирует отзыв и возвращает тональность: Positive или Negative.
    """
    prompt = (
        f"Проанализируй следующий отзыв и ответь только 'Positive' или 'Negative': {feedback}"
    )
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ты анализируешь эмоциональную окраску отзыва."},
            {"role": "user", "content": prompt},
        ],
    )
    answer = response.choices[0].message.content.strip()
    return "Positive" if "positive" in answer.lower() else "Negative"

async def answer_question(question: str, context: str, conversation_context: str) -> str:
    """
    Отвечает на вопросы пользователя с учетом контекста сообщества и истории диалога.
    """
    prompt = (
        f"Контекст сообщества: {context}\n"
        f"История диалога: {conversation_context}\n"
        f"Вопрос пользователя: {question}\n"
        f"Дай краткий и понятный ответ:"
    )
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ты помогаешь пользователю, отвечая на вопросы о сообществе."},
            {"role": "user", "content": prompt},
        ],
    )
    answer = response.choices[0].message.content.strip()
    return answer


def get_context() -> str:
    try:
        with open("community_context.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Информация о сообществе по умолчанию."
