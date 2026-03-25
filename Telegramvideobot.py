import os
import yt_dlp

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
user_links = {}

# 📩 Link kelganda
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
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

    await update.message.reply_text(
        "📥 Sifatni tanla:",
        reply_markup=reply_markup
    )
# 🎯 Tugma bosilganda
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    choice = query.data
    url = user_links.get(user_id)

    await query.message.reply_text("⏳ Yuklanmoqda...")

    try:
        if choice == "144":
            fmt = 'bestvideo[height<=144]+bestaudio/best'
        elif choice == "240":
            fmt = 'bestvideo[height<=240]+bestaudio/best'
        elif choice == "360":
            fmt = 'bestvideo[height<=360]+bestaudio/best'
        elif choice == "480":
            fmt = 'bestvideo[height<=480]+bestaudio/best'
        elif choice == "720":
            fmt = 'bestvideo[height<=720]+bestaudio/best'
        elif choice == "1080":
            fmt = 'bestvideo[height<=1080]+bestaudio/best'
        else:
            fmt = 'bestaudio'

        ydl_opts = {
            'format': fmt,
            'outtmpl': '%(title)s.%(ext)s',
            'noplaylist': True,
            'ffmpeg_location': r'C:\ffmpeg\bin',
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
# 🚀 BOTNI ISHGA TUSHIRISH
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(button_handler))

print("✅ Bot ishlayapti 🚀")
app.run_polling()
