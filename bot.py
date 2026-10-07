import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

API_TOKEN = '8817219207:AAEYnonur5Zy0Sg3wCxjpKqYVDrA_nO1qqQ'
GROUP_ID = -1004498687655

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# Ma'lumotlar bazasini yaratish (SQLite)
def init_db():
  conn = sqlite3.connect('murojaatlar.db')
  cursor = conn.cursor()
  cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        full_name TEXT,
        phone TEXT,
        message TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
  conn.commit()
  conn.close()


init_db()


class MurojaatState(StatesGroup):
  waiting_for_phone = State()
  waiting_for_message = State()


@dp.message(Command('start'))
async def send_welcome(message: Message, state: FSMContext):
  keyboard = ReplyKeyboardMarkup(
      keyboard=[
          [KeyboardButton(text='📱 Telefon raqamni yuborish', request_contact=True)]
      ],
      resize_keyboard=True,
      one_time_keyboard=True,
  )
  await message.reply(
      'Assalomu alaykum! Ushbu bot orqali rahbariyatga yoki guruhga **anonim'
      ' murojaat** yuborishingiz mumkin.\n\nXabaringiz guruhga hech qanday'
      " shaxsiy ma'lumotsiz (anonim tarzda) tashlanadi.\n\nDavom etish uchun"
      ' iltimos, pastdagi tugmani bosib **telefon raqamingizni yuboring** (bu'
      " ma'lumotlar bazasida maxfiy saqlanadi, guruhga ko'rinmaydi):",
      reply_markup=keyboard,
  )
  await state.set_state(MurojaatState.waiting_for_phone)


@dp.message(MurojaatState.waiting_for_phone, F.contact)
async def process_contact(message: Message, state: FSMContext):
  contact = message.contact
  phone = contact.phone_number

  await state.update_data(phone=phone)

  await message.reply(
      "Rahmat! Endi yubormoqchi bo'lgan **murojaat yoki taklifingizni yozib"
      " yuboring**:",
      reply_markup=ReplyKeyboardRemove(),
  )
  await state.set_state(MurojaatState.waiting_for_message)


@dp.message(MurojaatState.waiting_for_phone)
async def not_contact(message: Message):
  await message.reply(
      "Iltimos, pastdagi **'📱 Telefon raqamni yuborish'** tugmasini bosing."
  )


@dp.message(MurojaatState.waiting_for_message)
async def process_message(message: Message, state: FSMContext):
  user = message.from_user
  user_id = user.id
  username = f'@{user.username}' if user.username else "Yo'q"
  full_name = user.full_name
  text = message.text

  data = await state.get_data()
  phone = data.get('phone', 'Nomaʼlum')

  # 1. Guruhga anonim tarzda yuborish
  await bot.send_message(GROUP_ID, f'📩 **Yangi anonim murojaat:**\n\n{text}')

  # 2. Bazaga saqlash
  conn = sqlite3.connect('murojaatlar.db')
  cursor = conn.cursor()
  cursor.execute(
      'INSERT INTO messages (user_id, username, full_name, phone, message)'
      ' VALUES (?, ?, ?, ?, ?)',
      (user_id, username, full_name, phone, text),
  )
  conn.commit()
  conn.close()

  await message.reply(
      '✅ Murojaatingiz muvaffaqiyatli va anonim tarzda yuborildi! Rahmat.'
  )
  await state.clear()


async def main():
  await dp.start_polling(bot)


if __name__ == '__main__':
  asyncio.run(main())