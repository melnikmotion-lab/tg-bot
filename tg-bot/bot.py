    import asyncio
    import os
    import threading
    from urllib.parse import quote
    from flask import Flask
    from aiogram import Bot, Dispatcher, F
    from aiogram.types import (
        Message, ReplyKeyboardMarkup, KeyboardButton,
        InlineKeyboardMarkup, InlineKeyboardButton
    )
    from aiogram.filters import Command

    # Настройки бота
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable is not set")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    ADMIN_ID = -1003803972470

    # СЛОВАРЬ ДАННЫХ (Теперь для каждого юзера своя ячейка)
    user_data = {}

    # --- ТВОИ ОРИГИНАЛЬНЫЕ ДАННЫЕ (ИЗ bot.py) ---
    WELCOME_PHOTO = "AgACAgIAAxkBAAPnac0TZfCGiMWP1rxAB5KfIAcxLUsAAm8YaxsXzGhKc7biXPOKOEQBAAMCAAN5AAM6BA"
    # ... (здесь все твои result_images, questions, results, ID_TO_NAME и прочее из твоего файла)
    # Я сократил текст для краткости, но в твоем файле оставь всё как было в секциях === ВОПРОСЫ === и === РЕЗУЛЬТАТЫ ===
    # --------------------------------------------

    # [ВСТАВЬ СЮДА ВСЕ СВОИ ПЕРЕМЕННЫЕ: result_images, questions, results, question_11, NAME_TO_ID, ID_TO_NAME]

    # ТВОЯ ЛОГИКА ПОДСЧЕТА (Без изменений)
    def get_result(scores_by_name, answer_11=None):
        sorted_results = sorted(scores_by_name.items(), key=lambda x: x[1], reverse=True)
        first, second, third = sorted_results[0][1], sorted_results[1][1], sorted_results[2][1]
        if first == second == third:
            if answer_11 is None:
                top_three = [name for name, score in sorted_results[:3]]
                return "need_q11", {k: v for k, v in question_11.items() if k in top_three}
            return "single", answer_11
        elif first > second:
            return "single", sorted_results[0][0]
        return "double", f"{sorted_results[0][0]} + {sorted_results[1][0]}"

    # ВСЕ ТВОИ ФУНКЦИИ (notify_admin, result_to_key, send_final_result, send_question) ОСТАЮТСЯ ТАКИМИ ЖЕ

    # ОБНОВЛЕННЫЕ ОБРАБОТЧИКИ (Работают с user_data[user_id])
    @dp.message(Command("start"))
    async def start(message: Message):
        user_data[message.from_user.id] = {"current_question": 0, "scores": {1: 0, 2: 0, 3: 0, 4: 0}}
        # Твой код приветствия...
        await message.answer_photo(photo=WELCOME_PHOTO, caption="👋 Привет!...") 

    @dp.message(F.text == "🚀 Начать тест")
    async def start_test(message: Message):
        user_id = message.from_user.id
        user_data[user_id] = {"current_question": 0, "scores": {1: 0, 2: 0, 3: 0, 4: 0}}
        await send_question(message, 0)

    @dp.message(F.text.regexp(r"^[1-4]\."))
    async def handle_answer(message: Message):
        user_id = message.from_user.id
        if user_id not in user_data: return

        ans_num = int(message.text[0])
        user_data[user_id]["scores"][ans_num] += 1
        user_data[user_id]["current_question"] += 1

        if user_data[user_id]["current_question"] < len(questions):
            await send_question(message, user_data[user_id]["current_question"])
        else:
            await show_result(message, user_id)

    # ОСТАЛЬНЫЕ ФУНКЦИИ (show_result, handle_tiebreaker, show_offer) 
    # ПРОСТО КОПИРУЙ ИЗ СВОЕГО ОРИГИНАЛЬНОГО bot.py

    # === ЗАПУСК (Твой вариант с Flask) ===
    flask_app = Flask(__name__)
    @flask_app.route("/")
    def index(): return "Bot is running!", 200

    def run_flask():
        port = int(os.environ.get("BOT_PORT", 5000))
        flask_app.run(host="0.0.0.0", port=port)

    async def main():
        threading.Thread(target=run_flask, daemon=True).start()
        await dp.start_polling(bot)

    if __name__ == "__main__":
        asyncio.run(main())