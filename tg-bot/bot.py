import asyncio
import os
import threading
from urllib.parse import quote
from flask import Flask
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, LinkPreviewOptions,
    BotCommand, MenuButtonCommands, CallbackQuery
)
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is not set")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

ADMIN_ID = -1003803972470

async def notify_admin(text):
    try:
        await bot.send_message(ADMIN_ID, text)
    except Exception:
        pass

# === КЛАВИАТУРЫ ===

start_kb = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="🚀 Начать тест", callback_data="start_test")]]
)

subscribe_kb = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="✅ Подписка есть", callback_data="check_subscription")]]
)

offer_kb = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="📖 Узнать подробнее", callback_data="show_offer")]]
)

_consult_msg = quote("Привет! Я прошёл тест и готов узнать свой психотип на консультации 👋")

consultation_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text="✅ Записаться на консультацию",
            url=f"https://t.me/Alexey_melnik?text={_consult_msg}"
        )]
    ]
)

# === ТЕКСТЫ ===

consultation_text = """🔍 <b>Определение психотипа</b>

Вы получите ясность — которую не давали ни книги, ни психологи, ни годы самокопания

После консультации вы:
✨ Поймёте свою природу и предназначение — узнаете, что движет вами и без чего невозможно испытывать полноценное счастье.
💰 Направите энергию на финансовое процветание и привлечение возможностей.
💡 Обретёте внутреннее удовлетворение от деятельности, которая раскрывает ваш потенциал.
❤️ Узнаете, какой партнёр вам подходит для долгосрочных и гармоничных отношений.
📈 Поймёте свой путь эволюции и деградации: что поднимает вас на «пик», а что тянет в апатию и «слив» энергии.

📹 <b>Формат:</b> видеосозвон
⏱ <b>Длительность:</b> 2 часа
💰 <b>Стоимость:</b> <s>125$</s> → <b>100$</b> — в течение 24 часов после теста

В конце созвона вы получите запись консультации в личный чат в Telegram и возможность задавать любые вопросы о вашем психотипе в течение 14 дней 📅"""

# === КАРТИНКИ (file_id) ===

WELCOME_PHOTO = "AgACAgIAAxkBAAPnac0TZfCGiMWP1rxAB5KfIAcxLUsAAm8YaxsXzGhKc7biXPOKOEQBAAMCAAN5AAM6BA"

result_images = {
    (1,): "AgACAgIAAxkBAAMzac0IpSTnTPVT0rhhyBjvu8lyC7QAAhIWaxsLw2lKb5Le0x_RV4sBAAMCAAN5AAM6BA",
    (2,): "AgACAgIAAxkBAAMxac0Hn55Y4RUU6osxdNUf8_VskIIAAgsWaxsLw2lKlPJs6708cloBAAMCAAN5AAM6BA",
    (3,): "AgACAgIAAxkBAAPrac0Tj6JQX-RdTpraes0r64TW-Y4AAusZaxu1eWhKH1u0yufZsa0BAAMCAAN5AAM6BA",
    (4,): "AgACAgIAAxkBAAPsac0Tj7JE6SkRMpcnZnfNPTbuWr4AAuwZaxu1eWhK61m0rqxmH8ABAAMCAAN5AAM6BA",
    (1, 2): "AgACAgIAAxkBAAPjac0TORBB8y2mzMejgEqMmAsSuAQAAq0Xaxvo8WhKweDGGGjPiZoBAAMCAAN5AAM6BA",
    (1, 3): "AgACAgIAAxkBAAM0ac0JTA9LiWQZmg4sq8b0WGo4NywAAhUWaxsLw2lKvUgy1afbGBQBAAMCAAN5AAM6BA",
    (1, 4): "AgACAgIAAxkBAAPxac0TzWtqdxPhP6ZgSTSRwKbV-NIAAu0Zaxu1eWhK2rHzHvI_itUBAAMCAAN5AAM6BA",
    (2, 3): "AgACAgIAAxkBAAPyac0TzVPqSo9hi6tl8tCyfnN_bEYAAu8Zaxu1eWhKkkXPXzJywMkBAAMCAAN5AAM6BA",
    (2, 4): "AgACAgIAAxkBAAPzac0TzUh2pAkBv-I9op08uq4ZCCwAAvEZaxu1eWhKNfZdqpMoRwoBAAMCAAN5AAM6BA",
    (3, 4): "AgACAgIAAxkBAAP0ac0TzZfhRS6nK53KwgJkq6EJW6QAAvMZaxu1eWhKn5b0N5QDLJMBAAMCAAN5AAM6BA",
}

# === ВОПРОСЫ ===

questions = [
    {
        "question": "Вопрос 1\nЧто для меня важнее всего в жизни?",
        "answers": [
            "1. Стабильность, покой, безопасность",
            "2. Деньги, связи, возможности",
            "3. Власть, статус, признание",
            "4. Знания, смысл, духовный рост"
        ]
    },
    {
        "question": "Вопрос 2\nКак я принимаю решения?",
        "answers": [
            "1. Как все — не люблю рисковать",
            "2. Ищу выгоду и просчитываю шаги",
            "3. Сам, единолично — и готов отстаивать своё мнение",
            "4. Слушаю интуицию и ищу ответы внутри"
        ]
    },
    {
        "question": "Вопрос 3\nИдеальная работа для меня:",
        "answers": [
            "1. Понятная, стабильная, с чёткой оплатой",
            "2. Свобода, гибкий график, процент от результата",
            "3. Карьерный рост, своя сфера ответственности",
            "4. Полная свобода, без дедлайнов, признание таланта"
        ]
    },
    {
        "question": "Вопрос 4\nВ отношениях я ищу:",
        "answers": [
            "1. Того, кто не бросит и будет заботиться",
            "2. Хорошего партнёра для жизни и достатка",
            "3. Верность и преданность мне и моим целям",
            "4. Глубокого человека, на «одной волне» со мной"
        ]
    },
    {
        "question": "Вопрос 5\nЧто меня заряжает?",
        "answers": [
            "1. Спокойный день, всё по плану",
            "2. Новая сделка, новый проект, новые связи",
            "3. Победа, первое место, уважение",
            "4. Открытие, озарение, глубокое понимание чего-то"
        ]
    },
    {
        "question": "Вопрос 6\nЧто меня бесит больше всего?",
        "answers": [
            "1. Хаос, непредсказуемость, нестабильность",
            "2. Упущенные возможности и ограничения",
            "3. Когда не слушают и не уважают",
            "4. Поверхностность, глупость, нарушение принципов"
        ]
    },
    {
        "question": "Вопрос 7\nМоя сильная сторона:",
        "answers": [
            "1. Трудолюбие, мастерство, надёжность",
            "2. Коммуникабельность, гибкость, генерация идей",
            "3. Решимость, смелость, умение вести за собой",
            "4. Мудрость, независимость, широкое мировоззрение"
        ]
    },
    {
        "question": "Вопрос 8\nМоя слабая сторона:",
        "answers": [
            "1. Лень, инертность, страх перемен",
            "2. Поверхностность, жадность",
            "3. Бескомпромиссность, нетерпимость, жёсткость",
            "4. Отрешённость, мне сложно объяснить себя другим"
        ]
    },
    {
        "question": "Вопрос 9\nКак я отношусь к деньгам?",
        "answers": [
            "1. Главное, чтобы хватало на жизнь",
            "2. Деньги — это свобода и возможности",
            "3. Деньги — это власть и статус",
            "4. Деньги не главное, главное — смысл"
        ]
    },
    {
        "question": "Вопрос 10\nЧего я хочу от жизни по-настоящему?",
        "answers": [
            "1. Спокойной, предсказуемой жизни",
            "2. Процветания, удовольствия, достатка",
            "3. Признания, влияния, первенства",
            "4. Открытий, глубины, духовного роста"
        ]
    }
]

# === РЕЗУЛЬТАТЫ ===

results = {
    (1, 2): """У тебя есть склонности к природе
1 · Исполнителя и 2 · Предпринимателя

Исполнитель — это природа мастера и надёжного человека.
Стабильность, качество, умение делать своё дело
лучше других. Таких людей ценят, и на них держится мир.

Предприниматель — это природа того,
кто умеет делать деньги из идей и связей.
Новые проекты, процветание, рост — это его стихия.

Это две очень разные природы.

Даже если ты реализуешь обе свои природы — но они стоят не на своих местах, это всегда приводит к ощущению, что проживаешь чужую жизнь.

Именно поэтому так важно понять,
где твоя основная природа, а где дополнительная.

Основная — это твоя глубинная мотивация, то, как ты
«пробуешь этот мир на вкус». Твоё предназначение.
Без неё нет энергии, нет радости, нет смысла.

Дополнительная — это инструмент.
Профессия, роль, способ реализации.

Определить, где твой основной,
а где дополнительный психотип — по тесту невозможно.
Это видно только вживую —
по взгляду, речи и поведению.

Хочешь узнать свою природу
и с уверенностью идти по своему пути?""",

    (1, 3): """У тебя есть склонности к природе
1 · Исполнителя и 3 · Воина-руководителя

Исполнитель — это природа мастера и надёжного человека.
Стабильность, качество, умение делать своё дело
лучше других. Таких людей ценят, и на них держится мир.

Воин-руководитель — это природа лидера и защитника.
Тяга к влиянию, управлению, первенству.
Эти люди рождены вести за собой и менять порядок вещей.

Это две очень разные природы.

Даже если ты реализуешь обе свои природы — но они стоят не на своих местах, это всегда приводит к ощущению, что проживаешь чужую жизнь.

Именно поэтому так важно понять,
где твоя основная природа, а где дополнительная.

Основная — это твоя глубинная мотивация, то, как ты
«пробуешь этот мир на вкус». Твоё предназначение.
Без неё нет энергии, нет радости, нет смысла.

Дополнительная — это инструмент.
Профессия, роль, способ реализации.

Определить, где твой основной,
а где дополнительный психотип — по тесту невозможно.
Это видно только вживую —
по взгляду, речи и поведению.

Хочешь узнать свою природу
и с уверенностью идти по своему пути?""",

    (1, 4): """У тебя есть склонности к природе
1 · Исполнителя и 4 · Творца

Исполнитель — это природа мастера и надёжного человека.
Стабильность, качество, умение делать своё дело
лучше других. Таких людей ценят, и на них держится мир.

Творец — это природа свободного и утончённого мудреца.
Он хочет знать, как устроен мир, быть носителем духовных, научных
и культурных ценностей. Его увлекает не цель,
а сам вкус деятельности — познание, открытия, глубина.

Это две очень разные природы.

Даже если ты реализуешь обе свои природы — но они стоят не на своих местах, это всегда приводит к ощущению, что проживаешь чужую жизнь.

Именно поэтому так важно понять,
где твоя основная природа, а где дополнительная.

Основная — это твоя глубинная мотивация, то, как ты
«пробуешь этот мир на вкус». Твоё предназначение.
Без неё нет энергии, нет радости, нет смысла.

Дополнительная — это инструмент.
Профессия, роль, способ реализации.

Определить, где твой основной,
а где дополнительный психотип — по тесту невозможно.
Это видно только вживую —
по взгляду, речи и поведению.

Хочешь узнать свою природу
и с уверенностью идти по своему пути?""",

    (2, 3): """У тебя есть склонности к природе
2 · Предпринимателя и 3 · Воина-руководителя

Предприниматель — это природа того,
кто умеет делать деньги из идей и связей.
Новые проекты, процветание, рост — это его стихия.

Воин-руководитель — это природа лидера и защитника.
Тяга к влиянию, управлению, первенству.
Эти люди рождены вести за собой и менять порядок вещей.

Это две очень разные природы.

Даже если ты реализуешь обе свои природы — но они стоят не на своих местах, это всегда приводит к ощущению, что проживаешь чужую жизнь.

Именно поэтому так важно понять,
где твоя основная природа, а где дополнительная.

Основная — это твоя глубинная мотивация, то, как ты
«пробуешь этот мир на вкус». Твоё предназначение.
Без неё нет энергии, нет радости, нет смысла.

Дополнительная — это инструмент.
Профессия, роль, способ реализации.

Определить, где твой основной,
а где дополнительный психотип — по тесту невозможно.
Это видно только вживую —
по взгляду, речи и поведению.

Хочешь узнать свою природу
и с уверенностью идти по своему пути?""",

    (2, 4): """У тебя есть склонности к природе
2 · Предпринимателя и 4 · Творца

Предприниматель — это природа того,
кто умеет делать деньги из идей и связей.
Новые проекты, процветание, рост — это его стихия.

Творец — это природа свободного и утончённого мудреца.
Он хочет знать, как устроен мир, быть носителем духовных, научных
и культурных ценностей. Его увлекает не цель,
а сам вкус деятельности — познание, открытия, глубина.

Это две очень разные природы.

Даже если ты реализуешь обе свои природы — но они стоят не на своих местах, это всегда приводит к ощущению, что проживаешь чужую жизнь.

Именно поэтому так важно понять,
где твоя основная природа, а где дополнительная.

Основная — это твоя глубинная мотивация, то, как ты
«пробуешь этот мир на вкус». Твоё предназначение.
Без неё нет энергии, нет радости, нет смысла.

Дополнительная — это инструмент.
Профессия, роль, способ реализации.

Определить, где твой основной,
а где дополнительный психотип — по тесту невозможно.
Это видно только вживую —
по взгляду, речи и поведению.

Хочешь узнать свою природу
и с уверенностью идти по своему пути?""",

    (3, 4): """У тебя есть склонности к природе
3 · Воина-руководителя и 4 · Творца

Воин-руководитель — это природа лидера и защитника.
Тяга к влиянию, управлению, первенству.
Эти люди рождены вести за собой и менять порядок вещей.

Творец — это природа свободного и утончённого мудреца.
Он хочет знать, как устроен мир, быть носителем духовных, научных
и культурных ценностей. Его увлекает не цель,
а сам вкус деятельности — познание, открытия, глубина.

Это две очень разные природы.

Даже если ты реализуешь обе свои природы — но они стоят не на своих местах, это всегда приводит к ощущению, что проживаешь чужую жизнь.

Именно поэтому так важно понять,
где твоя основная природа, а где дополнительная.

Основная — это твоя глубинная мотивация, то, как ты
«пробуешь этот мир на вкус». Твоё предназначение.
Без неё нет энергии, нет радости, нет смысла.

Дополнительная — это инструмент.
Профессия, роль, способ реализации.

Определить, где твой основной,
а где дополнительный психотип — по тесту невозможно.
Это видно только вживую —
по взгляду, речи и поведению.

Хочешь узнать свою природу
и с уверенностью идти по своему пути?""",

    (1,): """У тебя есть склонности к природе
1 · Исполнителя

Исполнитель — это природа мастера и надёжного человека.
Стабильность, качество, умение делать своё дело
лучше других. Таких людей ценят, и на них держится мир.

По результатам теста твои ответы указывают только на одну природу.
Но это не означает, что она у тебя чистая.
Возможно, дополнительная природа просто скрыта —
или ты её пока не осознаёшь.

Определить это по тесту невозможно.
Это видно только вживую —
по взгляду, речи и поведению.

Хочешь узнать свою природу
и с уверенностью идти по своему пути?""",

    (2,): """У тебя есть склонности к природе
2 · Предпринимателя

Предприниматель — это природа того,
кто умеет делать деньги из идей и связей.
Новые проекты, процветание, рост — это его стихия.

По результатам теста твои ответы указывают только на одну природу.
Но это не означает, что она у тебя чистая.
Возможно, дополнительная природа просто скрыта —
или ты её пока не осознаёшь.

Определить это по тесту невозможно.
Это видно только вживую —
по взгляду, речи и поведению.

Хочешь узнать свою природу
и с уверенностью идти по своему пути?""",

    (3,): """У тебя есть склонности к природе
3 · Воина-руководителя

Воин-руководитель — это природа лидера и защитника.
Тяга к влиянию, управлению, первенству.
Эти люди рождены вести за собой и менять порядок вещей.

По результатам теста твои ответы указывают только на одну природу.
Но это не означает, что она у тебя чистая.
Возможно, дополнительная природа просто скрыта —
или ты её пока не осознаёшь.

Определить это по тесту невозможно.
Это видно только вживую —
по взгляду, речи и поведению.

Хочешь узнать свою природу
и с уверенностью идти по своему пути?""",

    (4,): """У тебя есть склонности к природе
4 · Творца

Творец — это природа свободного и утончённого мудреца.
Он хочет знать, как устроен мир, быть носителем духовных, научных
и культурных ценностей. Его увлекает не цель,
а сам вкус деятельности — познание, открытия, глубина.

По результатам теста твои ответы указывают только на одну природу.
Но это не означает, что она у тебя чистая.
Возможно, дополнительная природа просто скрыта —
или ты её пока не осознаёшь.

Определить это по тесту невозможно.
Это видно только вживую —
по взгляду, речи и поведению.

Хочешь узнать свою природу
и с уверенностью идти по своему пути?"""
}

# === ЛОГИКА ===

user_data = {}

NAME_TO_ID = {
    "Исполнитель": 1,
    "Предприниматель": 2,
    "Воин-руководитель": 3,
    "Творец": 4,
}

ID_TO_NAME = {v: k for k, v in NAME_TO_ID.items()}

TIEBREAKER_QUESTION = (
    "Вопрос 11. Где ты предпочитаешь проводить идеальный выходной?\n"
    "Выбери ближайший вариант:"
)

question_11 = {
    "Исполнитель": "Домашний уют, привычные дела, физический отдых и сон.",
    "Предприниматель": "Вечеринка, новые знакомства, активное движение и яркие впечатления.",
    "Воин-руководитель": "Соревнования, спорт, победа над собой или активное управление отдыхом группы.",
    "Творец": "Уединение, книга, природа или глубокое размышление в тишине.",
}

TIEBREAKER2_QUESTION = (
    "Вопрос 12. Как ты относишься к людям в своём окружении?\n"
    "Выбери ближайший вариант:"
)

question_12 = {
    "Исполнитель": "Ценю проверенных и надёжных людей.",
    "Предприниматель": "Легко завожу новые знакомства.",
    "Воин-руководитель": "Уважаю сильных и целеустремлённых.",
    "Творец": "Ценю глубину и понимание.",
}


def get_top2(scores_by_name):
    """Возвращает (first_name, second_name, tied_first, tied_second).
    tied_first — список имён с максимальным счётом.
    tied_second — список имён со вторым счётом (не входящих в tied_first).
    """
    sorted_results = sorted(scores_by_name.items(), key=lambda x: x[1], reverse=True)
    first_score = sorted_results[0][1]
    tied_first = [n for n, s in sorted_results if s == first_score]

    if len(tied_first) >= 2:
        return None, None, tied_first, []

    first_name = sorted_results[0][0]
    second_score = sorted_results[1][1]
    tied_second = [n for n, s in sorted_results[1:] if s == second_score]

    if len(tied_second) >= 2:
        return first_name, None, [], tied_second

    return first_name, sorted_results[1][0], [], []


def result_to_key(first, second):
    ids = tuple(sorted([NAME_TO_ID[first], NAME_TO_ID[second]]))
    return ids


def single_key(name):
    return (NAME_TO_ID[name],)


async def send_final_result(message, key, scores, user):
    result = results.get(key, "Результат не найден")
    photo_id = result_images.get(key)
    if photo_id:
        try:
            await message.answer_photo(photo=photo_id)
        except Exception:
            pass
    await message.answer(result, reply_markup=offer_kb)

    psychotype_names_genitive = {
        1: "Исполнителя", 2: "Предпринимателя",
        3: "Воина-руководителя", 4: "Творца"
    }
    psychotype_names = {
        1: "Исполнитель", 2: "Предприниматель",
        3: "Воин-руководитель", 4: "Творец"
    }
    result_label = " + ".join(f"{k} · {psychotype_names_genitive[k]}" for k in key)
    scores_text = "\n".join(
        f"{k} · {psychotype_names[k]}: {scores[k]}"
        for k in sorted(scores, key=lambda x: scores[x], reverse=True)
    )
    await notify_admin(
        f"✅ Тест пройден!\n"
        f"Имя: {user.full_name}\n"
        f"Username: @{user.username}\n\n"
        f"Результат: {result_label}\n\n"
        f"Разбивка:\n{scores_text}"
    )


def get_keyboard(answers):
    buttons = [[InlineKeyboardButton(text=answer, callback_data=f"answer_{answer[0]}")] for answer in answers]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def send_question(message, question_index):
    question = questions[question_index]
    await message.answer(question["question"], reply_markup=get_keyboard(question["answers"]))


async def finish_test(message, user_id, user):
    """Вызывается после 10 вопросов. Определяет результат или задаёт доп вопросы."""
    scores = user_data[user_id]["scores"]
    scores_by_name = {ID_TO_NAME[k]: v for k, v in scores.items()}

    # Случай 10 из 10
    sorted_results = sorted(scores_by_name.items(), key=lambda x: x[1], reverse=True)
    if sorted_results[0][1] == 10:
        key = single_key(sorted_results[0][0])
        await send_final_result(message, key, scores, user)
        return

    first_name, second_name, tied_first, tied_second = get_top2(scores_by_name)

    if tied_first:
        # Ничья за 1-е место среди 3+ → вопрос 11
        options = {v: k for k, v in question_11.items() if k in tied_first}
        user_data[user_id]["tb_stage"] = "first"
        user_data[user_id]["tb_candidates"] = tied_first
        buttons = [[InlineKeyboardButton(text=text, callback_data=f"tb_{name}")] for text, name in options.items()]
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer(TIEBREAKER_QUESTION, reply_markup=kb)
        return

    if tied_second:
        # Первый ясен, ничья за 2-е место → вопрос 11
        user_data[user_id]["tb_stage"] = "second"
        user_data[user_id]["tb_first"] = first_name
        user_data[user_id]["tb_candidates"] = tied_second
        options = {v: k for k, v in question_11.items() if k in tied_second}
        buttons = [[InlineKeyboardButton(text=text, callback_data=f"tb_{name}")] for text, name in options.items()]
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer(TIEBREAKER_QUESTION, reply_markup=kb)
        return

    # Всё ясно
    key = result_to_key(first_name, second_name)
    await send_final_result(message, key, scores, user)


# === HANDLERS ===

@dp.message(Command("start"))
async def start(message: Message):
    user_data[message.from_user.id] = {
        "current_question": 0,
        "scores": {1: 0, 2: 0, 3: 0, 4: 0},
        "subscribed": False
    }

    welcome_text = (
        "👋 Привет, я очень рад встрече с тобой!\n\n"
        "Сейчас тебя ждёт тест на психотипы.\n"
        "Отвечай честно — так результат будет точнее."
    )
    try:
        await message.answer_photo(photo=WELCOME_PHOTO, caption=welcome_text)
    except Exception:
        await message.answer(welcome_text)

    await message.answer(
        "Маленькая просьба, перед тем как пойдём дальше.\n\n"
        "Подпишись на мой <a href=\"https://t.me/Prirodo_ved\">ТГ-канал</a>, в котором я делюсь материалами "
        "по самопознанию и о том, как лучше понимать себя и других "
        "благодаря знанию о психотипах\n\n"
        "Как подпишешься — жми кнопку «Подписка есть» ✅",
        reply_markup=subscribe_kb,
        parse_mode="HTML",
        link_preview=LinkPreviewOptions(url="https://t.me/Prirodo_ved")
    )

    await notify_admin(
        f"👋 Новый пользователь!\n"
        f"Имя: {message.from_user.full_name}\n"
        f"Username: @{message.from_user.username}"
    )


CHANNEL_USERNAME = "@Prirodo_ved"


async def _do_check_subscription(user_id, send_fn):
    if user_id not in user_data:
        user_data[user_id] = {"current_question": 0, "scores": {1: 0, 2: 0, 3: 0, 4: 0}, "subscribed": False}

    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        is_subscribed = member.status in ("member", "administrator", "creator")
    except TelegramForbiddenError:
        is_subscribed = True
    except TelegramBadRequest as e:
        err = str(e).lower()
        is_subscribed = True if ("chat not found" in err or "bot is not a member" in err) else False
    except Exception:
        is_subscribed = True

    if not is_subscribed:
        await send_fn(
            "Похоже, ты ещё не подписан на канал 🙁\n\n"
            "Подпишись на мой <a href=\"https://t.me/Prirodo_ved\">ТГ-канал</a> и снова нажми «✅ Подписка есть»",
            reply_markup=subscribe_kb,
            parse_mode="HTML",
            link_preview=LinkPreviewOptions(url="https://t.me/Prirodo_ved")
        )
        return False

    user_data[user_id]["subscribed"] = True
    return True


@dp.message(F.text == "✅ Подписка есть")
async def handle_subscribed(message: Message):
    ok = await _do_check_subscription(message.from_user.id, message.answer)
    if ok:
        await message.answer("Отлично! Надеюсь, я смогу помочь тебе найти свой путь. Удачи! 🍀")
        await message.answer("Жми кнопку ниже, чтобы начать 👇", reply_markup=start_kb)


@dp.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery):
    await callback.answer()
    ok = await _do_check_subscription(callback.from_user.id, callback.message.answer)
    if ok:
        await callback.message.answer("Отлично! Надеюсь, я смогу помочь тебе найти свой путь. Удачи! 🍀")
        await callback.message.answer("Жми кнопку ниже, чтобы начать 👇", reply_markup=start_kb)


async def _do_start_test(message: Message, user_id: int):
    if user_id not in user_data or not user_data.get(user_id, {}).get("subscribed"):
        await message.answer(
            "Маленькая просьба, перед тем как пойдём дальше.\n\n"
            "Подпишись на мой <a href=\"https://t.me/Prirodo_ved\">ТГ-канал</a> и нажми «✅ Подписка есть»",
            reply_markup=subscribe_kb,
            parse_mode="HTML",
            link_preview=LinkPreviewOptions(url="https://t.me/Prirodo_ved")
        )
        return

    user_data[user_id]["current_question"] = 0
    user_data[user_id]["scores"] = {1: 0, 2: 0, 3: 0, 4: 0}
    # Чистим состояние тай-брейкера если было
    for key in ["tb_stage", "tb_first", "tb_candidates"]:
        user_data[user_id].pop(key, None)
    await send_question(message, 0)


@dp.message(F.text == "🚀 Начать тест")
async def start_test(message: Message):
    await _do_start_test(message, message.from_user.id)


@dp.callback_query(F.data == "start_test")
async def start_test_callback(callback: CallbackQuery):
    await callback.answer()
    await _do_start_test(callback.message, callback.from_user.id)


@dp.callback_query(F.data.startswith("answer_"))
async def handle_answer_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.answer()

    if user_id not in user_data:
        await callback.message.answer("Нажми /start чтобы начать тест")
        return

    answer_num = int(callback.data.split("_")[1])
    user_data[user_id]["scores"][answer_num] += 1
    user_data[user_id]["current_question"] += 1
    current = user_data[user_id]["current_question"]

    if current < len(questions):
        await send_question(callback.message, current)
    else:
        await finish_test(callback.message, user_id, callback.from_user)


@dp.callback_query(F.data.startswith("tb_"))
async def handle_tiebreaker_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.answer()

    if user_id not in user_data or "tb_stage" not in user_data.get(user_id, {}):
        await callback.message.answer("Нажми /start чтобы начать тест")
        return

    chosen = callback.data[len("tb_"):]
    stage = user_data[user_id]["tb_stage"]
    scores = user_data[user_id]["scores"]

    if stage == "first":
        # Выбрали первый психотип из тройной ничьи
        # Теперь нужно определить второго из оставшихся двух
        candidates = [n for n in user_data[user_id]["tb_candidates"] if n != chosen]
        user_data[user_id]["tb_stage"] = "second"
        user_data[user_id]["tb_first"] = chosen
        user_data[user_id]["tb_candidates"] = candidates
        options = {v: k for k, v in question_12.items() if k in candidates}
        buttons = [[InlineKeyboardButton(text=text, callback_data=f"tb_{name}")] for text, name in options.items()]
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.answer(TIEBREAKER2_QUESTION, reply_markup=kb)

    elif stage == "second":
        # Выбрали второй психотип
        first_name = user_data[user_id]["tb_first"]
        # Чистим состояние
        for key in ["tb_stage", "tb_first", "tb_candidates"]:
            user_data[user_id].pop(key, None)
        key = result_to_key(first_name, chosen)
        await send_final_result(callback.message, key, scores, callback.from_user)


@dp.callback_query(F.data == "show_offer")
async def show_offer_callback(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id

    await callback.message.answer(
        consultation_text,
        parse_mode="HTML",
        reply_markup=consultation_kb
    )

    await notify_admin(
        f"📖 Открыл оффер!\n"
        f"Имя: {callback.from_user.full_name}\n"
        f"Username: @{callback.from_user.username}"
    )

    if user_id in user_data:
        del user_data[user_id]


# === WEB SERVER (keep-alive) ===

flask_app = Flask(__name__)


@flask_app.route("/")
def index():
    return "Bot is running!", 200


def run_flask():
    port = int(os.environ.get("BOT_PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)


# === ЗАПУСК ===

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands([
        BotCommand(command="start", description="Начать тест 🚀")
    ])
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())
    threading.Thread(target=run_flask, daemon=True).start()
    await dp.start_polling(bot, drop_pending_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
