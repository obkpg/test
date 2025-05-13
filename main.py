import asyncio
import requests
import os

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from telethon import TelegramClient
from telethon.sessions import StringSession

# TELEGRAM API MA'LUMOTLARI
api_id = 29961525
api_hash = '8287129c125fce6db2fb4419c1aa54f3'
string = "1ApWapzMBuzA3vcQnj6wIiwzNUQVTss_K9ouKgs2d4S-kZE1XslbZl3T9kbOeVY8S1KZUOZCxBqp27PpWi4L3MsBtUOjQBclo76ySNXzcZLlqUBGofMfFdQ6eErbmPHj1lutppgfDbAo_8IasVz4Wys1ybl4iE7Eh-9F5lr-ZBA1wd6xGhodTnjAz-YYg_qmIV_s6ctvp5vT2Nnqng_My1OInRLj_4eThk8vYo7GcJWCJFwIk2jIlotnvLNbCM0pjNY9j1BIntB2qvGaOigk_asKRix_QxRPSiS2ky6DERWy_HW9lDdtps-EQW70kiHHYzq7d47VsgmsNIoSTwzDjPz35uygLQ3A="

# BOT TOKEN VA FOYDALANUVCHI ID’LAR
API_TOKEN = '7370977487:AAHEOqTT-UT672NphCL6jS1I7L3X0bX_ZYw'
ADMIN_ID = 6878918676
TO_USER_ID = "@obk_pg"

# AIORGRAM SETUP (3.7+ versiyaga mos)
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

# VIDEO YUKLASH FOIZLAR BILAN
async def download_video(url, filename, progress_callback):
    response = requests.get(url, stream=True)
    total = int(response.headers.get('content-length', 0))
    downloaded = 0

    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                percent = int(downloaded * 100 / total)
                await progress_callback(min(percent, 100))

# VIDEO YUBORISH TELETHON ORQALI
async def send_with_progress(client, file_path, entity, progress_callback):
    async def callback(current, total):
        percent = int(current * 100 / total)
        await progress_callback(min(percent, 100))

    await client.send_file(
        entity,
        file_path,
        caption="Mana video",
        progress_callback=callback
    )

# XABARNI QAYTA ISHLASH
@dp.message()
async def handle_link(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Sizga ruxsat berilmagan.")
        return

    url = message.text.strip()
    filename = url.split("/")[-1]

    status_msg = await message.answer("⏬ Yuklab olinmoqda: <b>0%</b>")

    last_percent = {"download": -5, "upload": -5}
    last_text = {"value": ""}

    async def safe_edit(text):
        if text != last_text["value"]:
            last_text["value"] = text
            try:
                await status_msg.edit_text(text)
            except Exception:
                pass  # ignore same text error or others

    async def update_download_progress(p):
        if p - last_percent["download"] >= 5:
            last_percent["download"] = p
            await safe_edit(f"⏬ Yuklab olinmoqda: <b>{p}%</b>")

    async def update_upload_progress(p):
        if p - last_percent["upload"] >= 5:
            last_percent["upload"] = p
            await safe_edit(f"⏫ Yuborilmoqda: <b>{p}%</b>")

    try:
        await download_video(url, filename, update_download_progress)
    except Exception as e:
        await safe_edit(f"❌ Yuklashda xatolik: {e}")
        return

    await safe_edit("⏫ Yuborilmoqda: <b>0%</b>")

    try:
        async with TelegramClient(StringSession(string), api_id, api_hash) as client:
            await send_with_progress(client, filename, TO_USER_ID, update_upload_progress)
        await safe_edit("✅ Video muvaffaqiyatli yuborildi.")
    except Exception as e:
        await safe_edit(f"❌ Yuborishda xatolik: {e}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

# BOTNI ISHGA TUSHURISH
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
