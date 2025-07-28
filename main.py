import asyncio
import logging
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import aiohttp
import nest_asyncio
import threading

# 🔐 Токены
BOT_TOKEN = "8190768971:AAGGSA5g-hUnrc34R8gOwwjfSez8BJ6Puz8"
CRYPTOBOT_TOKEN = "436380:AATIxpkr8ghHzhQq7psQ9YdjUXxLSQuAdUA"

# 🌐 Flask
app = Flask(__name__)

@app.route('/crypto', methods=['POST'])
def crypto_webhook():
    data = request.json
    print("\n📥 Получено уведомление от CryptoBot:", data)
    if data.get("status") == "success":
        user_id = data.get("user_id")
        amount = data.get("amount")
        print(f"✅ Оплата прошла: user_id={user_id}, amount={amount}")
    return "ok"

# 📎 Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 Баланс", callback_data="balance")],
        [InlineKeyboardButton("🚀 Купить хешрейт", callback_data="buy")],
        [InlineKeyboardButton("👥 Пригласить друга", callback_data="invite")],
        [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")],
        [InlineKeyboardButton("💸 Оплатить", callback_data="pay")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Добро пожаловать! Выберите действие:", reply_markup=reply_markup)

# 🔘 Обработка кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "pay":
        url = await create_invoice(query.from_user.id)
        if url:
            await query.edit_message_text(f"Перейдите по ссылке для оплаты:\n{url}")
        else:
            await query.edit_message_text("Ошибка при создании счета.")
    elif query.data == "balance":
        await query.edit_message_text("💰 Ваш текущий баланс: 0.001 BTC")
    elif query.data == "buy":
        await query.edit_message_text("🚀 Для покупки хешрейта перейдите на https://example.com")
    elif query.data == "invite":
        await query.edit_message_text("👥 Пригласите друга и получите 1% от его дохода.\nВаша ссылка: https://t.me/yourbot?start=123456")
    elif query.data == "help":
        await query.edit_message_text("ℹ️ Напишите /start, чтобы открыть меню снова. Поддержка: @support")

# 🧾 Создание счёта через CryptoBot
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

# 🚀 Запуск Telegram-бота
async def run_bot():
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CallbackQueryHandler(button_handler))
    print("✅ Telegram bot запущен")
    await app_bot.run_polling()

# 📦 Параллельный запуск Flask и Telegram
def start_flask():
    app.run(host="0.0.0.0", port=5000)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    nest_asyncio.apply()
    threading.Thread(target=start_flask).start()
    asyncio.run(run_bot())
