import asyncio
import logging
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import aiohttp
import nest_asyncio
import threading

BOT_TOKEN = "8190768971:AAGGSA5g-hUnrc34R8gOwwjfSez8BJ6Puz8"
CRYPTOBOT_TOKEN = "436380:AATIxpkr8ghHzhQq7psQ9YdjUXxLSQuAdUA"

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("💸 Оплатить", callback_data="pay"),
            InlineKeyboardButton("📊 Баланс", callback_data="balance"),
            InlineKeyboardButton("⚙️ Купить хешрейт", callback_data="buy_hashrate")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Добро пожаловать! Выберите действие:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "pay":
        url = await create_invoice(query.from_user.id)
        if url:
            await query.edit_message_text(f"Перейдите по ссылке для оплаты:\n{url}")
        else:
            await query.edit_message_text("Ошибка при создании счёта.")
    elif query.data == "balance":
        await query.edit_message_text("Ваш баланс: 0.00 USDT (заглушка)")
    elif query.data == "buy_hashrate":
        await query.edit_message_text("Купить хешрейт: функция в разработке")

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

async def run_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    print("✅ Telegram bot started")
    await application.run_polling()

def start_flask():
    app.run(host="0.0.0.0", port=5000)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    nest_asyncio.apply()
    threading.Thread(target=start_flask).start()
    asyncio.run(run_bot())
