from hashlib import md5
import logging
from database import Database
import utils
from aiogram import Bot, Dispatcher, executor, types
import charts
import perms
import economics
import datetime
import psutil

API_TOKEN = '5353342440:AAFGwIOKJY3MqhG-zvEbEjIMv-fHciFrZJM'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    logging.info(f"User {message.from_user.id} sent a /start command")
    await message.reply("""Привет, это бот для RLTGDPS.
Здесь ты можешь получать важные личные уведомления или как-либо взаимодействовать со своим аккаунтом.""")

@dp.message_handler(commands=['link'])
async def link_command(message: types.Message):
    if message.chat.type != "private":
        await message.reply("""Ошибка!
Использование данной команды допустимо только в личных сообщениях!""")
        return
    command = message.text.split(" ")
    if command.__len__() == 1:
        await message.reply("""Помощь по команде /link:
/link {имя аккаунта в игре}""")
        return
    db = Database(assoc=True)
    db.cursor.execute("SELECT * FROM accounts WHERE username LIKE %s", (command[1],))
    accs = db.cursor.fetchall()
    if accs.__len__() == 0:
        await message.reply("""Ошибка!
Такого аккаунта не существует.""")
        return
    acc = accs[0]

    if acc['temp_telegram_id'] != None:
        await message.reply("""Ошибка!
Ты уже запросил привязку. Зайди в игру, напиши пост с текстом /tgconfirm, чтобы подтвердить учётную запись.""")
        return
    if acc['telegram_id'] != None:
        await message.reply("""Ошибка!
Учётная запись этого аккаунта уже привязана.""")
        return

    db.cursor.execute("UPDATE accounts SET temp_telegram_id = %s WHERE ID = %s", (message.chat.id, acc['ID']))
    db.connection.commit()
    await message.reply("""Успешно!
Зайди в игру, напиши пост на аккаунте с текстом /tgconfirm, чтобы подтвердить учётную запись.""")

@dp.message_handler(commands=['password'])
async def change_password(message: types.Message):
    if message.chat.type != "private":
        await message.reply("""Ошибка!
Использование данной команды допустимо только в личных сообщениях!""")
        return
    command = message.text.split(" ", 1)
    user = utils.get_user_assoc_TG(message.from_user.id)
    if command.__len__() == 1:
        await message.reply("""Помощь по команде /password:
/password {новый пароль}""")
        return
    if user == None:
        await message.reply("""Ошибка!
Аккаунт не привязан. Привяжите командой /link.""")
        return
    newpass = str(command[1])
    newpasshash = md5(newpass.encode()).hexdigest()
    db = Database(assoc=True)
    db.cursor.execute("UPDATE accounts SET password = %s WHERE ID = %s", (newpasshash, user['ID']))
    db.connection.commit()
    await message.reply("""Успешно!
Зайди в игру и освежи данные аккаунта кнопкой \"Refresh Login\".""")

@dp.message_handler(commands=['username'])
async def change_username(message: types.Message):
    if message.chat.type != "private":
        await message.reply("""Ошибка!
Использование данной команды допустимо только в личных сообщениях!""")
        return
    command = message.text.split(" ", 1)
    user = utils.get_user_assoc_TG(message.from_user.id)
    if command.__len__() == 1:
        await message.reply("""Помощь по команде /username:
/username {новый ник}""")
        return
    if user == None:
        await message.reply("""Ошибка!
Аккаунт не привязан. Привяжите командой /link.""")
        return
    newusername = str(command[1])
    db = Database(assoc=True)
    db.cursor.execute("UPDATE accounts SET username = %s WHERE ID = %s", (newusername, user['ID']))
    db.connection.commit()
    await message.reply("""Успешно!
Зайди в игру и освежи данные аккаунта кнопкой \"Refresh Login\".""")

@dp.message_handler(commands=['transfer'])
async def transfer(message: types.Message):
    command = message.text.split(" ", 2)
    user = utils.get_user_assoc_TG(message.from_user.id)
    if command.__len__() < 3:
        await message.reply("""Помощь по команде /transfer:
/transfer {сколько_рубинов} {кому_ник}""")
        return
    if user == None:
        await message.reply("""Ошибка!
Аккаунт не привязан. Привяжите командой /link.""")
        return
    to_user = utils.get_user_assoc_by_username(command[2])
    amount = int(command[1])
    if amount <= 0:
        await message.reply("""Ошибка!
Невозможно перевести 0 или менее рубинов.""")
        return
    try:
        economics.transfer_money(user['ID'], to_user['ID'], amount)
    except economics.NoEnoughMoneyError:
        await message.reply("""Ошибка!
Недостаточно средств.""")
        return

@dp.message_handler(commands=['transactions'])
async def get_ta(message: types.Message):
    command = message.text.split(" ", 2)
    user = utils.get_user_assoc_TG(message.from_user.id)
    if user == None:
        await message.reply("""Ошибка!
Аккаунт не привязан. Привяжите командой /link.""")
        return
    
    text = """Вот все транзакции, связанные с тобой:
"""
    transactions = economics.get_transactions(user['ID'])
    for transaction in transactions:
        text += f"#{transaction['ID']}: {utils.get_username_by_id(transaction['account_from'])} перевел {transaction['amount']} рубинов {utils.get_username_by_id(transaction['account_to'])} в {datetime.datetime.fromtimestamp(transaction['timestamp']).strftime('%Y-%m-%d %H:%M:%S')} по МСК;\n"
    await message.reply(text)

@dp.message_handler(commands=['overview'])
async def get_overview(message: types.Message):
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    await message.reply(f"Процессор: {cpu}%, ОЗУ: {memory}")

@dp.message_handler(commands=['promote'])
async def promote(message: types.Message):
    command = message.text.split(" ", 2)
    user = utils.get_user_assoc_TG(message.from_user.id)
    if user == None:
        await message.reply("""Ошибка!
Аккаунт не привязан. Привяжите командой /link.""")
        return
    to_user = utils.get_user_assoc_by_username(command[1])
    mod_level = int(command[2])
    if "promote" not in perms.perms[user['mod_level']]:
        await message.reply("""Ошибка!
Нет прав.""")
        return
    db = Database(assoc=True)
    db.cursor.execute("UPDATE accounts SET mod_level = %s WHERE ID = %s", (mod_level, to_user['ID']))
    db.connection.commit()
    await message.reply(f"Модлвел обновлён у игрока {to_user['username']}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)