import os
import asyncio
import logging
import urllib.request
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Web server
web_app = Flask('')

@web_app.route('/')
def home():
    return "Bot status: Online"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)

def self_ping():
    app_url = os.environ.get("RENDER_EXTERNAL_URL")
    while True:
        try:
            asyncio.run(asyncio.sleep(600))
            if app_url:
                urllib.request.urlopen(app_url)
                print("Self ping successful!")
        except Exception as e:
            print(f"Ping error: {e}")

Thread(target=run_flask).start()
Thread(target=self_ping).start()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))

active_loops = {}

async def start_loop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ **Access Denied:** Sirf bot owner hi is command ko chala sakta hai.")
        return

    chat_id = update.effective_chat.id
    if active_loops.get(chat_id, False):
        await update.message.reply_text("⚠️ Loop pehle se chal raha hai! Stop karne ke liye `/stop_loop` likhein.")
        return

    if not context.args:
        await update.message.reply_text("❌ Kripya names ki list dein.\nExample: `/start_loop Name1, Name2, Name3`")
        return

    full_text = " ".join(context.args)
    name_list = [name.strip() for name in full_text.split(",") if name.strip()]

    if not name_list:
        await update.message.reply_text("❌ Kripya sahi names dein.")
        return

    active_loops[chat_id] = True
    await update.message.reply_text(f"✅ Loop chalu ho gaya hai!\n\n**Names:** {', '.join(name_list)}")

    count = 0
    while active_loops.get(chat_id, False):
        try:
            current_name = name_list[count % len(name_list)]
            await context.bot.set_chat_title(chat_id=chat_id, title=current_name)
            await update.message.reply_text(f"🤖 [Auto Update]: Group name badal kar **{current_name}** kar diya gaya hai!")
            count += 1
            await asyncio.sleep(15)
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(5)

async def stop_loop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    active_loops[update.effective_chat.id] = False
    await update.message.reply_text("⏹️ Loop rok diya gaya hai.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start_loop", start_loop))
    app.add_handler(CommandHandler("stop_loop", stop_loop))
    app.run_polling()

if __name__ == '__main__':
    main()
