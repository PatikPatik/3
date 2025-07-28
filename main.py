import logging
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.ext import Dispatcher
import os

BOT_TOKEN = "8190768971:AAGGSA5g-hUnrc34R8gOwwjfSez8BJ6Puz8"

# Flask App
app = Flask(__name__)

# Telegram Bot
bot = Bot(token=BOT_TOKEN)
application = Application.builder().token(BOT_TOKEN).build()
dispatcher = application.dispatcher

# Обработка команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💸 Оплатить", callback_data="pay")],
        [InlineKeyboardButton("💰 Баланс", callback_data="balance")],
        [InlineKeyboardButton("🚀 Купить хешрейт", callback_data="buy")],
        [InlineKeyboardButton("👥 Пригласить друга", callback_data="invite")],
        [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Выберите действие:", reply_markup=reply_markup)

# Обработка нажатий на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "pay":
        await query.edit_message_text("Платёжная система ещё настраивается.")
    elif data == "balance":
        await query.edit_message_text("Ваш баланс: 0.001 BTC")
    elif data == "buy":
        await query.edit_message_text("Вы можете купить хешрейт позже.")
    elif data == "invite":
        await query.edit_message_text("Пригласите друга и получите бонус.")
    elif data == "help":
        await query.edit_message_text("Это облачный майнинг-бот.")

# Регистрация обработчиков
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(button_handler))

# Обработка запросов от Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

# Установка webhook
@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    url = "https://three-0hx9.onrender.com/webhook"  # поменяй на свой Render URL
    success = bot.set_webhook(url=url)
    return f"Webhook set: {success}"

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=5000)
