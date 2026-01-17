import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.types import CallbackQuery
import re
from math import radians, sin, cos, sqrt, atan2

API_TOKEN = "8312195358:AAEp9IvJYoq1F1sAUOJctNnG1qMitHzDAKw"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ===== ЗАВДАННЯ =====
TASKS = {
    1: {
        "type": "photo_search",
        "title": "📸 ЗАВДАННЯ 1 — Street View Quest",
        "difficulty": "⭐⭐ Легкий",
        "key": "GREEN8",
        "photo": "https://github.com/user-attachments/assets/255ea37c-b5e6-4e7a-a11b-f9cbf38a2cc1",
        "question": "❓ Якого кольору двері будинку НАВПРОТИ? (позаду фотографа)",
        "fake_keys": ["GREEN", "DARKGREEN"],
        "points": 30,
        "hints": [
            "🔍 Підказка 1: Використовуйте Google Street View",
            "🔍 Підказка 2: Зверніть увагу на деталі архітектури, Німеччина",
            "🔍 Підказка 3: Правильна відповідь містить число"
        ],
        "hint_cost": 5
    },
    2: {
        "type": "photo_search",
        "title": "📸 ЗАВДАННЯ 2 — Історична Особа",
        "difficulty": "⭐⭐⭐ Середній",
        "key": "BATA1933",
        "photo": "https://github.com/user-attachments/assets/b0b809c4-85fd-40fb-ac85-cc08f94b75fb",
        "question": "❓ Хто ця людина і в якому році побудований монумент?",
        "fake_keys": ["BATA", "TOMAS", "TOMASBATA", "1933"],
        "points": 50,
        "hints": [
            "🔍 Підказка 1: Використовуйте Google Reverse Image Search, Чехія",
            "🔍 Підказка 2: Це відомий підприємець",
            "🔍 Підказка 3: Відповідь містить прізвище та рік побудови пам'ятника"
        ],
        "hint_cost": 10
    },
    3: {
        "type": "historical_manifest",
        "title": "📜 ЗАВДАННЯ 3 — Судновий Маніфест 1909",
        "difficulty": "⭐⭐⭐⭐ Складний",
        "photo": "https://github.com/user-attachments/assets/0ae9173f-ead7-495a-8107-c578249890db",
        "legend": (
            "На цьому історичному знімку 1909 року — група людей, які назавжди змінили науку про людську душу.\n"
            "Для візиту до США вони обрали лайнер 'George Washington'.\n\n"
            "Нас цікавить лише один із них — науковець із Відня, якому на момент цієї подорожі виповнилося 53 роки."
        ),
        "question": (
            "❓ Завдання:\n"
            "Знайдіть його запис у судновому маніфесті.\n"
            "Щоб підтвердити його особу, дайте відповідь:\n\n"
            "Кого він вказав як свого найближчого родича (Nearest Relative) у країні відправлення?\n\n"
            "📝 Формат відповіді: Ім'я Прізвище + підтвердження що це з маніфесту\n"

        ),
        "answer_keywords": ["MARTHA", "FREUD", "WIFE", "ДРУЖИНА"],
        "correct_answer": "MARTHA-FREUD-WIFE",
        "points": 100,
        "hints": [
            "🔍 Підказка 1: Це засновник психоаналізу",
            "🔍 Підказка 2: Шукай 'George Washington ship manifest 1909'",
            "🔍 Підказка 3: Використовуй heritage.statueofliberty.org",
            "🔍 Підказка 4: Його ініціали — S.F., повне ім'я - Sigmund Freud"
        ],
        "hint_cost": 15,
        "tools": " heritage.statueofliberty.org, Archive.org, Ellis Island Records"
    },
    4: {
        "type": "wayback_investigation",
        "title": "⏰ ЗАВДАННЯ 4 — Машина Часу",
        "difficulty": "⭐⭐⭐⭐ Складний",
        "legend": (
            "Facebook.com не завжди був соціальною мережею.\n"
            "Спочатку це був сайт для студентів Гарварду.\n\n"
            "Використай Wayback Machine для дослідження facebook.com:"
        ),
        "question": (
            "❓ Завдання:\n"
            "1. В якому році перший знімок сайту в архіві?\n"
            "2. Яка була оригінальна назва на головній сторінці?\n"
            "3. Скільки університетів було доступно в 2004 році? (1до5 / 5до10 / 10+)\n"
            "4. В якому році зникла приставка 'The' з назви?\n\n"
            "📝 Формат: РІК-НАЗВА-УНІВЕРИ-РІК\n"

        ),
        "answer_keywords": ["2004", "THEFACEBOOK", "2005"],
        "correct_answer": "2004-THEFACEBOOK-1ДО5-2005",
        "points": 100,
        "hints": [
            "🔍 Підказка 1: Відкрий archive.org/web/",
            "🔍 Підказка 2: Введи facebook.com та обери 2004 рік",
            "🔍 Підказка 3: Спочатку називався 'TheFacebook'",
            "🔍 Підказка 4: 'The' прибрали в 2005 році"
        ],
        "hint_cost": 15,
        "tools": "archive.org/web (Wayback Machine)"
    }
}

# ===== ДАНІ КОРИСТУВАЧІВ =====
USER_PROGRESS = {}
USER_HINTS = {}
USER_POINTS = {}
USER_ATTEMPTS = {}


# ===== ФУНКЦІЇ ПЕРЕВІРКИ =====

def validate_coordinates(user_input):
    """Перевірка формату координат"""
    pattern = r'^-?\d{1,2}\.?\d*,\s*-?\d{1,3}\.?\d*$'
    if not re.match(pattern, user_input):
        return None, "❌ Невірний формат!\n\n📝 Використовуйте: XX.XXXXX, YY.YYYYY\nПриклад: 37.334900, -122.009020"

    try:
        lat, lon = map(float, user_input.replace(' ', '').split(','))
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return None, "❌ Координати поза допустимими межами!"
        return (lat, lon), None
    except:
        return None, "❌ Помилка обробки координат"


def haversine_distance(coord1, coord2):
    """Розрахунок відстані між координатами в км"""
    R = 6371

    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def check_manifest_answer(user_input):
    """Перевірка відповіді з маніфесту"""
    user_upper = user_input.upper().replace(" ", "")

    # Ключові слова для перевірки
    has_martha = "MARTHA" in user_upper
    has_freud = "FREUD" in user_upper
    has_relation = "WIFE" in user_upper or "ДРУЖИНА" in user_upper or "ЖЕНА" in user_upper

    if has_martha and has_freud and has_relation:
        return True, "✅ ПРАВИЛЬНО! Це справді Martha Freud, дружина Зігмунда Фрейда!"

    hints = []
    if not has_martha:
        hints.append("💡 Ім'я починається з M")
    if not has_freud:
        hints.append("💡 Прізвище співпадає з прізвищем науковця")
    if not has_relation:
        hints.append("💡 Вкажи родинний зв'язок (wife/дружина)")

    if hints:
        return False, "⚠️ Неповна відповідь:\n" + "\n".join(hints)

    return False, "❌ Неправильно. Перевір маніфест уважніше!"

def check_coordinates(user_coords, correct_coords, tolerance_km):
    """Перевірка координат"""
    distance = haversine_distance(user_coords, correct_coords)

    if distance <= tolerance_km:
        return True, f"✅ ПРАВИЛЬНО!\n🎯 Точність: {int(distance * 1000)}м", distance
    elif distance <= 1:
        return False, f"⚠️ Близько! Відхилення: {distance:.2f} км", distance
    elif distance <= 10:
        return False, f"🔍 Ви в правильному районі! Відхилення: {distance:.1f} км", distance
    else:
        return False, f"❌ Неправильно. Відхилення: {distance:.0f} км", distance


def check_wayback_answer(user_input):
    """Перевірка Wayback відповіді"""
    user_upper = user_input.upper().replace(" ", "").replace("-", "|")
    parts = user_upper.split("|")

    if len(parts) != 4:
        return False, "❌ Формат: РІК-НАЗВА-УНІВЕРИ-РІК\nПриклад: 2004-TheFacebook-1до5-2005"

    year1_ok = parts[0] == "2004"
    name_ok = "THEFACEBOOK" in parts[1]
    unis_ok = "1" in parts[2] or "5" in parts[2]
    year2_ok = parts[3] in ["2005", "2006"]

    if all([year1_ok, name_ok, unis_ok, year2_ok]):
        return True, "✅ ЧУДОВА РОБОТА! Ти справжній цифровий археолог!"

    hints = []
    if not year1_ok: hints.append("💡 Перший архів з 2004")
    if not name_ok: hints.append("💡 Назва була 'TheFacebook'")
    if not unis_ok: hints.append("💡 Спочатку тільки Harvard")
    if not year2_ok: hints.append("💡 Ребрендинг в 2005")

    return False, "⚠️ Майже:\n" + "\n".join(hints)


# ===== КЛАВІАТУРИ =====

def get_hints_keyboard(level, user_id):
    """Створення клавіатури з підказками"""
    task = TASKS[level]
    hints_used = USER_HINTS.get(user_id, [])

    keyboard = []
    for i, hint in enumerate(task["hints"], 1):
        if i not in hints_used:
            keyboard.append([InlineKeyboardButton(
                text=f"💡 Підказка {i} (-{task['hint_cost']} балів)",
                callback_data=f"hint_{level}_{i}"
            )])

    if task["type"] in ["coordinates", "wayback_investigation", "historical_manifest"]:
        keyboard.append([InlineKeyboardButton(
            text="🛠️ Інструменти для пошуку",
            callback_data=f"tools_{level}"
        )])

    keyboard.append([InlineKeyboardButton(
        text="📊 Моя статистика",
        callback_data="stats"
    )])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ===== ХЕНДЛЕРИ =====

@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    USER_PROGRESS[user_id] = 1
    USER_HINTS[user_id] = []
    USER_POINTS[user_id] = 0
    USER_ATTEMPTS[user_id] = 0

    await message.answer(
        "🔍 <b>OSINT QUEST: ПОВНИЙ СПЕКТР</b>\n\n"
        "Ласкаво просимо в світ розвідки з відкритих джерел!\n\n"
        "📋 <b>Що тебе чекає:</b>\n"
        "• 📸 Пошук локацій за фото\n"
        "• 🛰️ Аналіз супутникових знімків\n"
        "• ⏰ Робота з архівними сайтами\n"
        "• 🕵️ Ідентифікація історичних осіб\n\n"
        "🎯 <b>Правила:</b>\n"
        "• Кожне завдання має свій формат відповіді\n"
        "• Використовуй інструменти OSINT\n"
        "• Підказки допоможуть, але зменшать бали\n\n"
        "🚀 Готовий? Розпочинаємо!",
        parse_mode="HTML"
    )

    await asyncio.sleep(1)
    await send_task(message, user_id, 1)


async def send_task(message: Message, user_id: int, level: int):
    """Відправка завдання"""
    if level not in TASKS:
        total_points = USER_POINTS.get(user_id, 0)
        total_attempts = USER_ATTEMPTS.get(user_id, 0)
        
        if total_points >= 200:
            rank = "🏆 ЕКСПЕРТ OSINT"
        elif total_points >= 150:
            rank = "🥇 ДОСВІДЧЕНИЙ АНАЛІТИК"
        elif total_points >= 100:
            rank = "🥈 АНАЛІТИК"
        else:
            rank = "🥉 ПОЧАТКІВЕЦЬ"
        
        await message.answer(
            f"🎉 <b>ВІТАЄМО!</b>\n\n"
            f"Ти успішно пройшов усі завдання OSINT Quest!\n\n"
            f"📊 <b>Твої результати:</b>\n"
            f"💰 Загальна кількість балів: {total_points}\n"
            f"🔄 Загальна кількість спроб: {total_attempts}\n"
            f"🎖️ Твій ранг: {rank}\n\n"
            f"Дякуємо за участь! 🔍",
            parse_mode="HTML"
        )
        return
    
    task = TASKS[level]
    
    # Формування тексту завдання
    if task["type"] == "photo_search":
        caption = (
            f"<b>{task['title']}</b>\n"
            f"Складність: {task['difficulty']}\n"
            f"Бали: {task['points']}\n\n"
            f"{task['question']}\n\n"
            f"📝 Відповідай ключовим словом у верхньому регістрі"
        )
    elif task["type"] == "coordinates":
        caption = (
            f"<b>{task['title']}</b>\n"
            f"Складність: {task['difficulty']}\n"
            f"Бали: {task['points']}\n\n"
            f"<b>Легенда:</b>\n{task['legend']}\n\n"
            f"<b>{task['question']}</b>\n\n"
            f"📝 Формат: XX.XXXXX, YY.YYYYY"
        )
    else:
        caption = (
            f"<b>{task['title']}</b>\n"
            f"Складність: {task['difficulty']}\n"
            f"Бали: {task['points']}\n\n"
            f"<b>Легенда:</b>\n{task['legend']}\n\n"
            f"{task['question']}"
        )
    
    # Відправка
    if "photo" in task:
        try:
            await message.answer_photo(
                photo=task["photo"],
                caption=caption,
                parse_mode="HTML",
                reply_markup=get_hints_keyboard(level, user_id)
            )
        except Exception as e:
            await message.answer(
                f"{caption}\n\n⚠️ Помилка завантаження фото: {e}",
                parse_mode="HTML",
                reply_markup=get_hints_keyboard(level, user_id)
            )
    else:
        await message.answer(
            caption,
            parse_mode="HTML",
            reply_markup=get_hints_keyboard(level, user_id)
        )


@dp.callback_query(lambda c: c.data.startswith("hint_"))
async def process_hint(callback: CallbackQuery):
    """Обробка підказок"""
    user_id = callback.from_user.id
    _, level_str, hint_num_str = callback.data.split("_")
    level = int(level_str)
    hint_num = int(hint_num_str)

    task = TASKS[level]

    if user_id not in USER_HINTS:
        USER_HINTS[user_id] = []

    if hint_num in USER_HINTS[user_id]:
        await callback.answer("⚠️ Ти вже використав цю підказку!", show_alert=True)
        return

    USER_HINTS[user_id].append(hint_num)
    USER_POINTS[user_id] = USER_POINTS.get(user_id, 0) - task["hint_cost"]

    await callback.message.answer(
        f"{task['hints'][hint_num - 1]}\n\n"
        f"💰 Знято балів: {task['hint_cost']}\n"
        f"📊 Твої бали: {USER_POINTS[user_id]}",
        parse_mode="HTML"
    )

    await callback.message.edit_reply_markup(reply_markup=get_hints_keyboard(level, user_id))
    await callback.answer()


@dp.callback_query(lambda c: c.data.startswith("tools_"))
async def show_tools(callback: CallbackQuery):
    """Показ інструментів"""
    _, level_str = callback.data.split("_")
    level = int(level_str)
    task = TASKS[level]

    tools_text = f"🛠️ <b>Рекомендовані інструменти:</b>\n\n{task['tools']}"

    if task["type"] == "coordinates":
        tools_text += (
            "\n\n<b>Методологія:</b>\n"
            "1️⃣ Google Earth - пошук об'єктів\n"
            "2️⃣ Аналізуйте форму будівель\n"
            "3️⃣ ПКМ → 'What's here?' для координат"
        )
    elif task["type"] == "wayback_investigation":
        tools_text += (
            "\n\n<b>Методологія:</b>\n"
            "1️⃣ Відкрий archive.org/web\n"
            "2️⃣ Введи домен\n"
            "3️⃣ Обери рік зі знімками\n"
            "4️⃣ Досліджуй історію сайту"
        )
    elif task["type"] == "historical_manifest":
        tools_text += (
            "\n\n<b>Методологія:</b>\n"
            "1️⃣ Визначте історичну особу (психоаналіз, Відень, 53 роки в 1909)\n"
            "2️⃣ Шукай 'George Washington ship manifest 1909'\n"
            "3️⃣ Використай ancestry.com або familysearch.org\n"
            "4️⃣ Знайди графу 'Nearest Relative'\n"
            "5️⃣ Вкажи ім'я, прізвище і родинний зв'язок"
        )

    await callback.message.answer(tools_text, parse_mode="HTML")
    await callback.answer()


@dp.callback_query(lambda c: c.data == "stats")
async def show_stats(callback: CallbackQuery):
    """Статистика"""
    user_id = callback.from_user.id
    level = USER_PROGRESS.get(user_id, 1)
    points = USER_POINTS.get(user_id, 0)
    attempts = USER_ATTEMPTS.get(user_id, 0)
    hints_used = len(USER_HINTS.get(user_id, []))

    await callback.message.answer(
        f"📊 <b>ТВОЯ СТАТИСТИКА</b>\n\n"
        f"🎯 Поточний рівень: {level}\n"
        f"💰 Набрано балів: {points}\n"
        f"🔄 Спроб зроблено: {attempts}\n"
        f"💡 Підказок використано: {hints_used}",
        parse_mode="HTML"
    )
    await callback.answer()


@dp.message()
async def handle_message(message: Message):
    """Обробка відповідей"""
    user_id = message.from_user.id
    level = USER_PROGRESS.get(user_id, 1)

    if level not in TASKS:
        await message.answer("🎉 Ти вже пройшов усі завдання!")
        return

    task = TASKS[level]
    user_input = message.text.strip()
    USER_ATTEMPTS[user_id] = USER_ATTEMPTS.get(user_id, 0) + 1

    is_correct = False
    feedback = ""

    # Перевірка залежно від типу завдання
    if task["type"] == "photo_search":
        # Перевірка ключового слова
        user_key = user_input.upper().replace(" ", "")
        correct_key = task["key"].upper()
        fake_keys = [k.upper() for k in task.get("fake_keys", [])]

        print(f"DEBUG: user_key='{user_key}', correct_key='{correct_key}'")  # Відладка

        if user_key == correct_key:
            is_correct = True
            feedback = "✅ ПРАВИЛЬНО!"
        elif user_key in fake_keys:
            await message.answer(
                "⚠️ Ти близько, але це пастка. Перевір деталі уважніше.",
                reply_markup=get_hints_keyboard(level, user_id)
            )
            return
        else:
            await message.answer(
                f"❌ Невірний ключ. Спробуй ще раз.\n\n🔄 Спроб: {USER_ATTEMPTS[user_id]}",
                reply_markup=get_hints_keyboard(level, user_id)
            )
            return

    elif task["type"] == "coordinates":
        # Перевірка координат
        coords, error = validate_coordinates(user_input)
        if error:
            await message.answer(error)
            return

        correct_coords = (task["correct_lat"], task["correct_lon"])
        is_correct, feedback, distance = check_coordinates(coords, correct_coords, task["tolerance_km"])

    elif task["type"] == "historical_manifest":
        # Перевірка маніфесту
        is_correct, feedback = check_manifest_answer(user_input)

    elif task["type"] == "wayback_investigation":
        # Перевірка Wayback відповіді
        is_correct, feedback = check_wayback_answer(user_input)

    if is_correct:
        # Правильна відповідь
        points_earned = task["points"]
        USER_POINTS[user_id] = USER_POINTS.get(user_id, 0) + points_earned

        result_text = f"{feedback}\n\n💰 <b>Отримано балів:</b> +{points_earned}\n📊 <b>Всього балів:</b> {USER_POINTS[user_id]}"

        if task["type"] == "coordinates":
            result_text += f"\n\n📍 <b>Локація:</b> {task['location_name']}"
        elif task["type"] == "wayback_investigation":
            result_text += "\n\n⏰ <b>Історія:</b> TheFacebook → Facebook (2005)"
        elif task["type"] == "historical_manifest":
            result_text += "\n\n📜 <b>Особа:</b> Зігмунд Фрейд, засновник психоаналізу\n🚢 <b>Лайнер:</b> George Washington, 1909"

        await message.answer(result_text, parse_mode="HTML")

        # Наступний рівень
        next_level = level + 1
        USER_PROGRESS[user_id] = next_level
        USER_HINTS[user_id] = []

        await asyncio.sleep(2)
        await send_task(message, user_id, next_level)
    else:
        await message.answer(
            f"{feedback}\n\n🔄 Спроб: {USER_ATTEMPTS[user_id]}",
            reply_markup=get_hints_keyboard(level, user_id)
        )


@dp.message(Command("reset"))
async def cmd_reset(message: Message):
    """Перезапуск"""
    user_id = message.from_user.id
    USER_PROGRESS[user_id] = 1
    USER_HINTS[user_id] = []
    USER_POINTS[user_id] = 0
    USER_ATTEMPTS[user_id] = 0

    await message.answer("🔄 Прогрес скинуто! /start для перезапуску")


async def main():
    print("🔍 OSINT Quest Bot запускається…")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":

    asyncio.run(main())

