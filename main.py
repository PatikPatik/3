import logging
import threading
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

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
def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("💸 Оплатить", callback_data="pay")],
        [InlineKeyboardButton("💰 Баланс", callback_data="balance")],
        [InlineKeyboardButton("⚙️ Купить хешрейт", callback_data="buy_hashrate")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Добро пожаловать! Выберите действие:", reply_markup=reply_markup)

# 🔘 Обработка кнопок
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    if query.data == "pay":
        url = create_invoice(query.from_user.id)
        if url:
            query.edit_message_text(f"Перейдите по ссылке для оплаты:\n{url}")
        else:
            query.edit_message_text("Ошибка при создании счёта.")
    
    elif query.data == "balance":
        query.edit_message_text("💰 Ваш баланс: 0 USDT")  # Здесь можно подключить реальный расчёт
    elif query.data == "buy_hashrate":
        query.edit_message_text("⚙️ Купить хешрейт пока недоступно.")

# 🧾 Создание счёта через CryptoBot
import requests
def create_invoice(user_id: int):
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
    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        print("🧾 Ответ от CryptoBot:", data)
        if data.get("ok"):
            return data["result"]["pay_url"]
    except Exception as e:
        print("Ошибка при создании счёта:", e)
    return None

# 🚀 Запуск Telegram-бота
def run_bot():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Telegram бот запущен")
    updater.start_polling()
    updater.idle()

# 📦 Параллельный запуск Flask и Telegram
def start_flask():
    app.run(host="0.0.0.0", port=5000)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    threading.Thread(target=start_flask).start()
    run_bot()
