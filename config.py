from dotenv import load_dotenv
import os

load_dotenv()

# Токен бота, URL для подключения к базе и API-ключ OpenAI
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Файл с контекстом сообщества
COMMUNITY_CONTEXT_FILE = os.getenv("COMMUNITY_CONTEXT_FILE", "community_context.txt")

# Ссылка на чат сообщества
CHAT_LINK = os.getenv("CHAT_LINK", "https://t.me/my_chat")
