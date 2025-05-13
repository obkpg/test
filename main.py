import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import requests
import os

# Telegram API ma'lumotlaringiz
api_id = 29961525
api_hash = '8287129c125fce6db2fb4419c1aa54f3'
string = "1ApWapzMBuzA3vcQnj6wIiwzNUQVTss_K9ouKgs2d4S-kZE1XslbZl3T9kbOeVY8S1KZUOZCxBqp27PpWi4L3MsBtUOjQBclo76ySNXzcZLlqUBGofMfFdQ6eErbmPHj1lutppgfDbAo_8IasVz4Wys1ybl4iE7Eh-9F5lr-ZBA1wd6xGhodTnjAz-YYg_qmIV_s6ctvp5vT2Nnqng_My1OInRLj_4eThk8vYo7GcJWCJFwIk2jIlotnvLNbCM0pjNY9j1BIntB2qvGaOigk_asKRix_QxRPSiS2ky6DERWy_HW9lDdtps-EQW70kiHHYzq7d47VsgmsNIoSTwzDjPz35uygLQ3A="

# Bot token va admin ID
API_TOKEN = '7785923994:AAH7zxeKsQdN1t4it-ffyXZ6sxvmjGA6_gc'
ADMIN_ID = 6878918676
TO_USER_ID = "@obk_pg"

# Video yuklash funksiyasi
def download_video(url, filename):
    print("Video yuklanmoqda...")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print("Yuklandi.")

# Foydalanuvchi xabarini qayta ishlovchi handler
async def handle_link(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Sizga ruxsat berilmagan.")
        return

    url = message.text.strip()
    filename = url.split("/")[-1]

    await message.answer("Video yuklanmoqda...")
    try:
        download_video(url, filename)
    except Exception as e:
        await message.answer(f"Yuklashda xatolik: {e}")
        return

    await message.answer("Video yuborilmoqda...")

    try:
        with TelegramClient(StringSession(string), api_id, api_hash) as client:
            client.send_file(TO_USER_ID, filename, caption="Mana video")
        await message.answer("Yuborildi.")
    except Exception as e:
        await message.answer(f"Yuborishda xatolik: {e}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

# Botni ishga tushuruvchi funksiya
async def main():
    async with Bot(token=API_TOKEN) as bot:
        dp = Dispatcher()
        dp.message.register(handle_link)
        await dp.start_polling(bot)

# Ishga tushirish
if __name__ == "__main__":
    asyncio.run(main())
