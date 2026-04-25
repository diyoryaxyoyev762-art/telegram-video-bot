import os
import yt_dlp
import threading
from flask import Flask

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
user_links = {}

app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot ishlayapti"

# 📩 Link kelganda
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.text:
        url = update.message.text

    elif update.message.caption:
        url = update.message.caption

    else:
        await update.message.reply_text("❌ Link topilmadi")
        return

    user_links[update.message.from_user.id] = url

    keyboard = [
        [InlineKeyboardButton("🎬 144p", callback_data="144")],
        [InlineKeyboardButton("🎬 240p", callback_data="240")],
        [InlineKeyboardButton("🎬 360p", callback_data="360")],
        [InlineKeyboardButton("🎬 480p", callback_data="480")],
        [InlineKeyboardButton("🎬 720p", callback_data="720")],
        [InlineKeyboardButton("🎬 1080p", callback_data="1080")],
        [InlineKeyboardButton("🎵 Audio", callback_data="audio")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📥 Sifatni tanla:", reply_markup=reply_markup)

# 🎯 Tugma bosilganda
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    choice = query.data
    url = user_links.get(user_id)

    await query.message.reply_text("⏳ Yuklanmoqda...")

    try:
        fmt = 'bestaudio' if choice == "audio" else f'bestvideo[height<={choice}]+bestaudio/best'

        ydl_opts = {
            'format': fmt,
            'outtmpl': '%(title)s.%(ext)s',
            'noplaylist': True,
            'merge_output_format': 'mp4'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)

        size = os.path.getsize(file_name)

        if size > 50 * 1024 * 1024:
            await query.message.reply_text("❌ Fayl katta")
        else:
            await query.message.reply_document(open(file_name, "rb"))

        os.remove(file_name)

    except Exception as e:
        await query.message.reply_text(f"❌ Xatolik: {e}")

# 🚀 Botni ishga tushirish
def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()
   app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("✅ Bot ishlayapti 🚀")
    app.run_polling()

threading.Thread(target=run_bot).start()

# 🌐 Flask port ochadi
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)
