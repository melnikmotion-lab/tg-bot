import asyncio
import os
from flask import Flask
from threading import Thread
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command

# Токен берем из переменных окружения
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Словарь для хранения состояния каждого пользователя
user_data = {}

# Твои вопросы (пример структуры, проверь свои тексты!)
QUESTIONS = [
    {"text": "Вопрос 1: Как вы оцениваете свой уровень энергии?", "options": ["Низкий", "Средний", "Высокий"], "points": [1, 2, 3]},
    {"text": "Вопрос 2: Как вы принимаете решения?", "options": ["Логика", "Интуиция"], "points": [5, 10]}
]

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    # При старте обнуляем данные конкретно для этого пользователя
    user_data[message.from_user.id] = {"score": 0, "q_index": 0}
    await send_question(message.from_user.id)

async def send_question(user_id):
    data = user_data.get(user_id)
    if data["q_index"] < len(QUESTIONS):
        q = QUESTIONS[data["q_index"]]
        # Создаем кнопки для текущего вопроса
        kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text=opt, callback_data=f"ans_{i}")] 
            for i, opt in enumerate(q["options"])
        ])
        await bot.send_message(user_id, q["text"], reply_markup=kb)
    else:
        # Финальный расчет
        score = data["score"]
        await bot.send_message(user_id, f"Тест окончен! Ваш результат: {score}")

@dp.callback_query(F.data.startswith("ans_"))
async def handle_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in user_data:
        await callback.answer("Начните тест заново через /start")
        return

    # Получаем индекс ответа
    ans_index = int(callback.data.split("_")[1])
    q_index = user_data[user_id]["q_index"]

    # Прибавляем баллы
    user_data[user_id]["score"] += QUESTIONS[q_index]["points"][ans_index]
    user_data[user_id]["q_index"] += 1

    await callback.message.delete() # Убираем старый вопрос
    await send_question(user_id)

# Flask для поддержки жизни сервера (как у тебя было)
app = Flask(__name__)
@app.route('/')
def index(): return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

async def main():
    Thread(target=run_flask).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())