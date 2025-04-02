import requests
from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from datetime import datetime
import pytz

import os
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        location = update.message.location
        lat = location.latitude
        lon = location.longitude

        geo_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        geo_resp = requests.get(geo_url, headers={'User-Agent': 'Mozilla/5.0'})
        geo_data = geo_resp.json()

        address = geo_data.get("address", {})
        display_name = geo_data.get("display_name", "Nomaʼlum joy")
        city = address.get("city") or address.get("town") or address.get("village") or address.get("state") or "Nomaʼlum shahar"
        country = address.get("country", "Nomaʼlum davlat")

        tz_url = f"http://api.aladhan.com/v1/timeZone/{lat}/{lon}"
        tz_resp = requests.get(tz_url).json()
        timezone = tz_resp["data"]["timezone"]
        local_time = datetime.now(pytz.timezone(timezone)).strftime("%H:%M %d-%m-%Y")

        prayer_url = f"https://api.aladhan.com/v1/timings?latitude={lat}&longitude={lon}&method=2"
        prayer_resp = requests.get(prayer_url).json()
        timings = prayer_resp["data"]["timings"]

        message = (
            f"Manzil: {display_name}\n"
            f"Shahar: {city}, Davlat: {country}\n"
            f"Mahalliy vaqt: {local_time}\n\n"
            f"Namoz vaqtlari:\n"
            f"Fajr: {timings['Fajr']}\n"
            f"Sunrise: {timings['Sunrise']}\n"
            f"Dhuhr: {timings['Dhuhr']}\n"
            f"Asr: {timings['Asr']}\n"
            f"Maghrib: {timings['Maghrib']}\n"
            f"Isha: {timings['Isha']}"
        )

        await update.message.reply_text(message)

    except Exception as e:
        await update.message.reply_text("Xatolik yuz berdi. Qaytadan urinib ko‘ring.")
        print(f"Xatolik: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location_button = KeyboardButton("Joylashuvni yuborish", request_location=True)
    keyboard = ReplyKeyboardMarkup([[location_button]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        "Assalomu alaykum! Iltimos, joylashuvingizni yuboring:",
        reply_markup=keyboard
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    print("Bot ishga tushdi...")
    app.run_polling()

if name == "main":
    main()
