import asyncio
import os
import aiohttp

from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# Konfiguratsiya (os.environ yoki .env tavsiya etiladi)
api_id = 29961525
api_hash = '8287129c125fce6db2fb4419c1aa54f3'
string = "1ApWapzMBuzA3vcQnj6wIiwzNUQVTss_K9ouKgs2d4S-kZE1XslbZl3T9kbOeVY8S1KZUOZCxBqp27PpWi4L3MsBtUOjQBclo76ySNXzcZLlqUBGofMfFdQ6eErbmPHj1lutppgfDbAo_8IasVz4Wys1ybl4iE7Eh-9F5lr-ZBA1wd6xGhodTnjAz-YYg_qmIV_s6ctvp5vT2Nnqng_My1OInRLj_4eThk8vYo7GcJWCJFwIk2jIlotnvLNbCM0pjNY9j1BIntB2qvGaOigk_asKRix_QxRPSiS2ky6DERWy_HW9lDdtps-EQW70kiHHYzq7d47VsgmsNIoSTwzDjPz35uygLQ3A="

# BOT TOKEN VA FOYDALANUVCHI ID’LAR
API_TOKEN = '8042306409:AAFcy6RnbiGFiOksSFlkndCRMd-X3EZKiiE'
ADMIN_ID = 6878918676
TO_USER_ID = "@meva_url"

MONITOR_CHANNEL = -1002674988964  # @test_db kanalining ID raqami ("@" bilan emas, -100 bilan boshlanadi)

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()
dp.include_router(router)

queue = asyncio.Queue()
active_users = set()

# Yuklab olish funksiyasi
async def download_video(url, filename, progress_callback):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            total = int(resp.headers.get('Content-Length', 0))
            downloaded = 0
            with open(filename, 'wb') as f:
                async for chunk in resp.content.iter_chunked(8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    percent = int(downloaded * 100 / total)
                    await progress_callback(min(percent, 100))

# Yuborish funksiyasi
async def send_with_progress(client, file_path, to_user, progress_callback, cap):
    file_size = os.path.getsize(file_path)

    def callback(current, total):
        percent = int(current * 100 / file_size)
        asyncio.create_task(progress_callback(min(percent, 100)))  # Asinxron progress ni chaqirish

    await client.send_file(to_user, file_path, progress_callback=callback, caption=cap)
# Asosiy video ishlovchi funksiya
async def process_video(user_id, url, message):
    filename = url.split("/")[-1]
    status_msg = await message.answer("⏬ Navbatda kutyapti...")

    last_percent = {"download": -5, "upload": -5}
    last_text = {"value": ""}

    async def safe_edit(text):
        if text != last_text["value"]:
            last_text["value"] = text
            try:
                await status_msg.edit_text(text)
            except:
                pass

    async def update_download_progress(p):
        if p - last_percent["download"] >= 5:
            last_percent["download"] = p
            await safe_edit(f"⏬ Yuklab olinmoqda: <b>{p}%</b>")

    async def update_upload_progress(p):
        if p - last_percent["upload"] >= 5:
            last_percent["upload"] = p
            await safe_edit(f"⏫ Yuborilmoqda: <b>{p}%</b>")

    try:
        await safe_edit("⏬ Yuklab olinmoqda: <b>0%</b>")
        await download_video(url, filename, update_download_progress)
    except Exception as e:
        await safe_edit(f"❌ Yuklashda xatolik: {e}")
        return

    await safe_edit("⏫ Yuborilmoqda: <b>0%</b>")
    try:
        async with TelegramClient(StringSession(string), api_id, api_hash) as client:
            await send_with_progress(client, filename, TO_USER_ID, update_upload_progress, user_id)
        await safe_edit("✅ Video muvaffaqiyatli yuborildi.")
    except Exception as e:
        await safe_edit(f"❌ Yuborishda xatolik: {e}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

# Navbat uchun ishchi task
async def queue_worker():
    while True:
        user_id, url, message = await queue.get()
        try:
            await process_video(user_id, url, message)
        finally:
            active_users.discard(user_id)
            queue.task_done()

# /start komandasi
@router.message(F.text == "/start")
async def start_handler(message: Message):
    await message.answer("Salom! Menga video havolasini yuboring, men uni yuklab kanalga yuboraman.")

# Kanal post kuzatuvchi
@router.channel_post()
async def monitor_channel_post(message: Message):
    if message.chat.id == MONITOR_CHANNEL and message.video:
        caption = message.caption or "Yo'q"
        await bot.copy_message(chat_id=caption, from_chat_id=MONITOR_CHANNEL, message_id=message.message_id)

# Video so‘rovi
@router.message()
async def handle_request(message: Message):
    user_id = message.from_user.id
    url = message.text.strip()

    if url.startswith("/cancel"):
        if user_id in active_users:
            active_users.discard(user_id)
            await message.answer("❌ So‘rovingiz bekor qilindi.")
        else:
            await message.answer("ℹ️ Sizda faol so‘rov yo‘q.")
        return

    if user_id in active_users:
        await message.answer("❗ Sizda faol so‘rov bor. Iltimos, uni tugashini kuting.")
        return

    active_users.add(user_id)
    await queue.put((user_id, url, message))
    navbat_joyi = queue.qsize()
    await message.answer(f"✅ So‘rovingiz navbatga qo‘shildi. Navbatda: {navbat_joyi}")

# Botni ishga tushurish
async def main():
    asyncio.create_task(queue_worker())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
