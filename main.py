import logging
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import aiohttp
import asyncio

# === НАСТРОЙКИ ===
BOT_TOKEN = "8190768971:AAGGSA5g-hUnrc34R8gOwwjfSez8BJ6Puz8"
CRYPTOBOT_TOKEN = "436380:AATIxpkr8ghHzhQq7psQ9YdjUXxLSQuAdUA"
WEBHOOK_URL = "https://three-0hx9.onrender.com/webhook"  # 🚨 Замени на свой актуальный URL Render!

# === Flask приложение ===
app = Flask(__name__)
application: Application = None  # глобальная переменная для Telegram-бота

# === Вебхук от CryptoBot ===
@app.route("/crypto", methods=["POST"])
def crypto():
    data = request.json
    print("📥 Уведомление от CryptoBot:", data)

    if data.get("status") == "success":
        user_id = data.get("user_id")
        amount = data.get("amount")
        print(f"✅ Оплата прошла: user_id={user_id}, amount={amount}")
        # Здесь можно начислить бонусы или уведомить пользователя

    return "ok"

# === Вебхук для Telegram ===
@app.route("/webhook", methods=["POST"])
async def telegram_webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot=application.bot)
    await application.process_update(update)
    return "ok"

# === Обработка команды /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 Баланс", callback_data="balance")],
        [InlineKeyboardButton("🚀 Купить хешрейт", callback_data="buy")],
        [InlineKeyboardButton("👥 Пригласить друга", callback_data="invite")],
        [InlineKeyboardButton("💸 Оплатить", callback_data="pay")],
        [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Выберите действие:", reply_markup=markup)

# === Обработка нажатий на кнопки ===
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data == "balance":
        await query.edit_message_text("Ваш баланс: 0.001 BTC")
    elif data == "buy":
        await query.edit_message_text("Купить хешрейт можно на сайте ...")
    elif data == "invite":
        await query.edit_message_text("Пригласите друга и получите бонус 1%.")
    elif data == "pay":
        url = await create_invoice(query.from_user.id)
        if url:
            await query.edit_message_text(f"Перейдите по ссылке для оплаты:\n{url}")
        else:
            await query.edit_message_text("Ошибка при создании счёта.")
    elif data == "help":
        await query.edit_message_text("Бот для облачного майнинга. Используйте кнопки.")

# === Создание счёта в CryptoBot ===
async def create_invoice(user_id: int) -> str | None:
    url = "https://pay.crypt.bot/api/createInvoice"
    headers = {
        "Crypto-Pay-API-Token": CRYPTOBOT_TOKEN,
        "Content-Type": "application/json"
    }
    json_data = {
        "asset": "USDT",
        "amount": 1.00,
        "description": "Оплата подписки",
        "payload": str(user_id),
        "hidden_message": "Спасибо за оплату!",
        "paid_btn_name": "openChannel",
        "paid_btn_url": "https://t.me/yourchannel",
        "allow_comments": False,
        "allow_anonymous": False,
        "expires_in": 900
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=json_data) as response:
            data = await response.json()
            print("🧾 Ответ от CryptoBot:", data)
            if data.get("ok"):
                return data["result"]["pay_url"]
            return None

# === Запуск Telegram-бота и установка вебхука ===
async def main():
    global application
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_buttons))

    bot: Bot = application.bot
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(url=WEBHOOK_URL)
    print("✅ Вебхук установлен:", WEBHOOK_URL)

    # Не запускаем polling, только Flask обрабатывает
    # await application.run_polling()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
    app.run(host="0.0.0.0", port=5000)
