import asyncio
import pandas as pd
from aiogram import Bot, types, Dispatcher
from aiogram.types import parseMode
from aiogram.filters import Command

# Конфигурация
TELEGRAM_BOT_TOKEN = "7911955909:AAHoLeKySJ875fTsnk7WjOrTXRj_tAUGlHE"  # Замените на токен вашего бота

# Инициализация бота
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Загрузка базы знаний
data = pd.read_csv("BB_data.csv")  # Замените на путь к вашему CSV файлу

# Функция для поиска ответа на вопрос
def find_answer(question: str):
    # Ищем строку, где вопрос наиболее похож на заданный
    for index, row in data.iterrows():
        if row['question'].lower() in question.lower():
            return row['answer']
    return "Извините, я не знаю ответа на этот вопрос."

# Обработка команды /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer("Привет! Задайте мне вопрос, и я постараюсь на него ответить.")

# Обработка сообщений (вопросов)
@dp.message()
async def handle_message(message: types.Message):
    user_question = message.text
    answer = find_answer(user_question)
    await message.answer(answer, parse_mode=parseMode.MARKDOWN)

# Основной запуск
async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
