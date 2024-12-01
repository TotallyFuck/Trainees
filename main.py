import asyncio
import openai
from supabase import create_client, Client
from aiogram import Bot, types, Router, Dispatcher
from aiogram.filters import Command
from aiogram import F
import pandas as pd

# Конфигурация
SUPABASE_URL = "https://ntffubxxftdrtobsejta.supabase.co"  # Замените на ваш URL
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50ZmZ1Ynh4ZnRkcnRvYnNlanRhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzE2OTcwODQsImV4cCI6MjA0NzI3MzA4NH0.uliXXU8Y7uEfrGAWWf3iBLfqsd25itIQuSIunUnYHhE"  # Замените на ваш API ключ
TELEGRAM_BOT_TOKEN = "7911955909:AAHoLeKySJ875fTsnk7WjOrTXRj_tAUGlHE"  # Замените на токен вашего бота
OPENAI_API_KEY = "sk-abcd1234qrstuvwxabcd1234qrstuvwxabcd1234"  # Замените на ваш API ключ OpenAI

# Инициализация Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Инициализация бота
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Инициализация Router
router = Router()

# Хранение состояния пользователей
user_sessions = {}

# Загрузка данных для обработки вопросов
data = pd.read_csv("BB_data.csv")  # Ожидается, что в CSV есть столбцы 'question' и 'answer'

# Устанавливаем ключ API для OpenAI
openai.api_key = OPENAI_API_KEY


# Функция для получения ответа от GPT-3
def get_gpt3_answer(user_question: str):
    response = openai.Completion.create(
        engine="text-davinci-003",  # Используем модель GPT-3. Можно использовать другие модели OpenAI
        prompt=user_question,
        max_tokens=150,
        temperature=0.7,
    )
    return response.choices[0].text.strip()


# Авторизация: Шаг 1 — запрос номера телефона
@router.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Добро пожаловать! Введите ваш номер телефона:")


# Авторизация: Шаг 2 — проверка номера телефона и запроса пароля
@router.message(F.text & ~F.text.regexp(r"^\d+$"))
async def request_password(message: types.Message):
    user_id = message.from_user.id
    number = message.text

    # Сохраняем введенный номер телефона в сессию
    user_sessions[user_id] = {"number": number}
    await message.answer("Введите пароль:")


# Авторизация: Шаг 3 — проверка пароля и логин
@router.message(F.text & F.text.regexp(r"^\d+$"))
async def login_user(message: types.Message):
    user_id = message.from_user.id
    password = message.text

    if user_id in user_sessions:
        number = user_sessions[user_id]["number"]

        # Проверяем пользователя в базе данных Supabase
        response = supabase.table("users").select("*").eq("number", number).eq("password", password).execute()

        if response.data:
            # Авторизация успешна
            user = response.data[0]  # Данные пользователя
            fullname = user["fullname"]
            await message.answer(f"Добро пожаловать, {fullname}!")
            
            # user_sessions[user_id] = {"logged_in": True}

            # Удаляем сессию из памяти для безопасности
            # del user_sessions[user_id]

            # Устанавливаем в сессии пользователя флаг авторизации
            user_sessions[user_id] = {"logged_in": True}

            # Запрашиваем вопрос
            await message.answer("Теперь, задайте свой вопрос, и я постараюсь на него ответить:")
        else:
            # Неверные данные
            await message.answer("Неправильный номер телефона или пароль. Попробуйте снова.")
            await message.answer("Введите ваш номер телефона:")
    else:
        await message.answer("Введите номер телефона сначала через команду /start.")


# Обработка вопроса после авторизации
@router.message(F.text)
async def handle_user_question(message: types.Message):
    user_id = message.from_user.id

    if user_id in user_sessions and user_sessions[user_id].get("logged_in"):
        # Получаем вопрос пользователя
        user_question = message.text

        # Получаем ответ от GPT-3
        answer = get_gpt3_answer(user_question)

        # Отправляем ответ
        await message.answer(answer)
    else:
        await message.answer("Вы не авторизованы. Введите /start для начала.")


# Основной запуск
async def main():
    print("Бот запущен!")
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
