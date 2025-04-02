import requests
import os
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from datetime import datetime
import pytz

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Render.com dagi environment variable

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        location = update.message.location
        lat = location.latitude
        lon = location.longitude

        # 1) Nominatim orqali geolokatsiya
        try:
            geo_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
            geo_resp = requests.get(geo_url, headers={'User-Agent': 'Mozilla/5.0'})
            geo_resp.raise_for_status()  # 4xx/5xx xatoni ushlab qolish
            geo_data = geo_resp.json()
        except Exception as e:
            print("GEO request error:", e)
            raise

        address = geo_data.get("address", {})
        display_name = geo_data.get("display_name", "Nomaʼlum joy")
        city = address.get("city") or address.get("town") or address.get("village") or address.get("state") or "Nomaʼlum shahar"
        country = address.get("country", "Nomaʼlum davlat")

        # 2) AlAdhan orqali vaqt zonasi
        try:
            tz_url = f"http://api.aladhan.com/v1/timeZone/{lat}/{lon}"
            tz_resp = requests.get(tz_url, headers={'User-Agent': 'Mozilla/5.0'})
            tz_resp.raise_for_status()
            tz_json = tz_resp.json()
            # "data" va "timezone" bor-yo‘qligini tekshiramiz
            if "data" not in tz_json or "timezone" not in tz_json["data"]:
                print("TimeZone data missing in response:", tz_json)
                raise ValueError("Timezone ma'lumoti topilmadi.")
            timezone = tz_json["data"]["timezone"]
        except Exception as e:
            print("TimeZone request error:", e)
            raise

        # Mahalliy vaqtni hisoblash
        try:
            local_time = datetime.now(pytz.timezone(timezone)).strftime("%H:%M %d-%m-%Y")
        except Exception as e:
            print("Local time parse error:", e)
            raise

        # 3) AlAdhan orqali namoz vaqtlarini olish
        try:
            prayer_url = f"https://api.aladhan.com/v1/timings?latitude={lat}&longitude={lon}&method=2"
            prayer_resp = requests.get(prayer_url, headers={'User-Agent': 'Mozilla/5.0'})
            prayer_resp.raise_for_status()
            prayer_json = prayer_resp.json()
            if "data" not in prayer_json or "timings" not in prayer_json["data"]:
                print("Prayer data missing in response:", prayer_json)
                raise ValueError("Namoz vaqtlari topilmadi.")
            timings = prayer_json["data"]["timings"]
        except Exception as e:
            print("Prayer times request error:", e)
            raise

        # Yakuniy javob matni
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
        # Asosiy xatolik
        print("Xatolik:", e)
        await update.message.reply_text("Kechirasiz, xatolik yuz berdi. Qaytadan urinib ko‘ring.")

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    button = KeyboardButton("Joylashuvni yuborish", request_location=True)
    keyboard = ReplyKeyboardMarkup([[button]], resize_keyboard=True, one_time_keyboard=True)
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

if __name__ == "__main__":
    main()
