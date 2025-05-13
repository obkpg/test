import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
import requests
import os

API_TOKEN = '8188443282:AAF_SommfUjIbhlpoaqD9iG8z8kKfBXAjCQ'
ADMIN_ID = 6878918676  # o'zingizning Telegram ID'ingiz

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message()
async def handle_link(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Sizga ruxsat berilmagan.")
        return

    url = message.text.strip()
    filename = url.split("/")[-1]

    try:
        response = requests.get(url)
        with open(filename, "wb") as f:
            f.write(response.content)

        await message.answer("Video yuklandi, yuborilmoqda...")
        await message.answer_video(types.FSInputFile(filename))

        os.remove(filename)
    except Exception as e:
        await message.answer(f"Xatolik: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())