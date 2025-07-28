import asyncio
import logging
from flask import Flask, request
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import aiohttp
import nest_asyncio
import threading

# 🔐 Токены
BOT_TOKEN = "8190768971:AAGGSA5g-hUnrc34R8gOwwjfSez8BJ6Puz8"
CRYPTOBOT_TOKEN = "436380:AATIxpkr8ghHzhQq7psQ9YdjUXxLSQuAdUA"

# 🌐 Flask сервер
app = Flask(__name__)

@app.route("/")
def index():
    return "Бот работает!"

# 📩 Webhook CryptoBot
@app.route("/crypto", methods=["POST"])
def crypto_webhook():
    data = request.json
    print("📥 Получено уведомление от CryptoBot:", data)
    if data.get("status") == "success":
        user_id = data.get("user_id")
        amount = data.get("amount")
        print(f"✅ Оплата прошла: user_id={user_id}, amount={amount}")
    return "ok"

# 📍 /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 Баланс", callback_data="balance")],
        [InlineKeyboardButton("🚀 Купить хешрейт", callback_data="buy")],
        [InlineKeyboardButton("👥 Пригласить друга", callback_data="invite")],
        [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")],
        [InlineKeyboardButton("💸 Оплатить", callback_data="pay")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

# 🎯 Обработка нажатий
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    print(f"🔘 Нажата кнопка: {data}")

    if data == "balance":
        await query.edit_message_text("Ваш текущий баланс: 0.001 BTC")
    elif data == "buy":
        await query.edit_message_text("Для покупки хешрейта перейдите на сайт ...")
    elif data == "invite":
        await query.edit_message_text("Пригласите друга и получите бонус 1% от его дохода.")
    elif data == "help":
        await query.edit_message_text("Это бот для облачного майнинга. Напишите /start, чтобы начать.")
    elif data == "pay":
        url = await create_invoice(query.from_user.id)
        if url:
            await query.edit_message_text(f"💳 Перейдите по ссылке для оплаты:\n{url}")
        else:
            await query.edit_message_text("❌ Ошибка при создании счёта.")

# 🧾 Счёт через CryptoBot
async def create_invoice(user_id: int):
    url = "https://pay.crypt.bot/api/createInvoice"
    headers = {
        "Content-Type": "application/json",
        "Crypto-Pay-API-Token": CRYPTOBOT_TOKEN
    }
    payload = {
        "asset": "USDT",
        "amount": 1.00,
        "description": "Оплата подписки",
        "hidden_message": "Спасибо за оплату!",
        "paid_btn_name": "openChannel",
        "paid_btn_url": "https://t.me/yourchannel",
        "payload": str(user_id),
        "allow_comments": False,
        "allow_anonymous": False,
        "expires_in": 900
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            result = await resp.json()
            print("🧾 Ответ от CryptoBot:", result)
            if result.get("ok"):
                return result["result"]["pay_url"]
            return None

# 🚀 Telegram бот
async def run_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    print("✅ Telegram bot запущен")
    await application.run_polling()

# 🧵 Запуск Flask + Bot
def run_flask():
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    nest_asyncio.apply()
    threading.Thread(target=run_flask).start()
    asyncio.run(run_bot())
