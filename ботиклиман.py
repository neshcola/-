import asyncio
import json
import os
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

TOKEN = "8516795655:AAHfSA9wS3pf4GcOAFxD052HCBMZKrtdIBE"
# ЗАМЕНИ ЭТУ ССЫЛКУ на свою ссылку от GitHub Pages
WEB_APP_URL = "https://neshcola.github.io/-/"
DATA_FILE = "users.json"

dp = Dispatcher()
users = {}

def load_data():
    global users
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

load_data()

def get_main_kb():
    kb = [
        [KeyboardButton(text="🥤 Открыть лавку", web_app=WebAppInfo(url=WEB_APP_URL))],
        [KeyboardButton(text="/stats")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@dp.message(Command("start"))
async def start(mes: Message):
    uid = str(mes.chat.id)
    if uid not in users:
        users[uid] = {'Деньги': 50, 'Лимоны': 0, 'Сахар': 0, 'Лимонад': 0, 'lvl': 1, 'total_made': 0}
        save_data()
    await mes.answer("Добро пожаловать в бизнес! Используй кнопку меню или команду /start.", reply_markup=get_main_kb())

@dp.message(lambda msg: msg.text == "/buy_lemon")
async def buy_lemon(mes: Message):
    uid = str(mes.chat.id)
    if users[uid]['Деньги'] >= 10:
        users[uid]['Деньги'] -= 10
        users[uid]['Лимоны'] += 1
        save_data()
        await mes.answer(f"🍋 Лимон куплен! Баланс: {users[uid]['Деньги']}р.")
    else:
        await mes.answer("Недостаточно денег!")

@dp.message(lambda msg: msg.text == "/buy_sugar")
async def buy_sugar(mes: Message):
    uid = str(mes.chat.id)
    if users[uid]['Деньги'] >= 5:
        users[uid]['Деньги'] -= 5
        users[uid]['Сахар'] += 100
        save_data()
        await mes.answer(f"🍬 Сахар куплен! Всего: {users[uid]['Сахар']}г.")
    else:
        await mes.answer("Недостаточно денег!")

@dp.message(lambda msg: msg.text == "/make_lemonade")
async def make_lemonade(mes: Message):
    uid = str(mes.chat.id)
    u = users[uid]
    if u['Лимоны'] >= 1 and u['Сахар'] >= 100:
        u['Лимоны'] -= 1
        u['Сахар'] -= 100
        u['total_made'] += 1
        
        is_spoiled = u['total_made'] > 1 and random.random() < 0.15
        price = 30 + (u['lvl'] * 5)
        
        if is_spoiled:
            earned = int(price * 0.3)
            res = f"🤢 Лимонад испортился! Выручка всего {earned}р."
        else:
            earned = price
            u['Лимонад'] += 1
            res = f"🥤 Успех! Продано за {earned}р."
        
        u['Деньги'] += earned
        u['lvl'] = (u['Лимонад'] // 5) + 1
        save_data()
        await mes.answer(res)
    else:
        await mes.answer("Не хватает ингредиентов!")

@dp.message(Command("stats") or (lambda msg: msg.text == "/stats"))
async def stats(mes: Message):
    u = users.get(str(mes.chat.id))
    await mes.answer(f"💰 Деньги: {u['Деньги']}\n🌟 Уровень: {u['lvl']}\n🍋 Лимоны: {u['Лимоны']}\n🍬 Сахар: {u['Сахар']}")

async def main():
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
