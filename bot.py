from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
import datetime

import os
from dotenv import load_dotenv
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
SERVICE, DATE, TIME, PAYMENT, PHONE = range(5)

# Клавиатуры
services_keyboard = ReplyKeyboardMarkup(
    [
        ["🔧 Замена масла", "🛞 Шиномонтаж"],
        ["🔍 Диагностика", "⚙️ Ремонт двигателя"],
        ["🚘 Кузовной ремонт", "🧼 Мойка авто"],
        ["⬅️ Назад", "❌ Отмена"],
    ],
    resize_keyboard=True
)

time_keyboard = ReplyKeyboardMarkup(
    [
        ["09:00", "11:00", "13:00"],
        ["15:00", "17:00", "19:00"],
        ["⬅️ Назад", "❌ Отмена"],
    ],
    resize_keyboard=True
)

main_keyboard = ReplyKeyboardMarkup(
    [
        ["📝 Записаться"],
        ["📋 Услуги", "📞 Контакты"],
        ["📖 Мои записи"],   # ← Новая кнопка
    ],
    resize_keyboard=True
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚗 Добро пожаловать в AutoService Motor!\n\n"
        "Выбери действие:",
        reply_markup=main_keyboard
    )


async def show_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 Наши услуги:\n\n"
        "🔧 Замена масла\n"
        "🛞 Шиномонтаж\n"
        "🔍 Диагностика авто\n"
        "⚙️ Ремонт двигателя\n"
        "🚘 Кузовной ремонт\n"
        "🧼 Мойка авто"
    )


async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📞 Контакты:\n\n"
        "☎️ Телефон: +998 90 123 45 67\n"
        "📍 Адрес: Ташкент\n"
        "🕘 Работаем: 09:00–20:00"
    )


# ====================== ИСТОРИЯ ЗАПИСЕЙ ======================
async def show_my_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bookings = context.user_data.get("bookings", [])
    
    if not bookings:
        await update.message.reply_text(
            "📖 У вас пока нет записей.",
            reply_markup=main_keyboard
        )
        return

    text = "📖 **Ваши записи:**\n\n"
    for i, booking in enumerate(bookings, 1):
        text += (
            f"{i}. 🛠 {booking['service']}\n"
            f"   📅 {booking['date']} в {booking['time']}\n"
            f"   💰 {booking['payment']}\n"
            f"   📞 {booking['phone']}\n\n"
        )

    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_keyboard)


# ====================== ЗАПИСЬ ======================
async def booking_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Выбери услугу:",
        reply_markup=services_keyboard
    )
    return SERVICE


async def choose_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text in ["⬅️ Назад", "❌ Отмена"]:
        await start(update, context)
        return ConversationHandler.END

    context.user_data["service"] = text
    await update.message.reply_text(
        "📅 Напишите дату записи (в формате ДД.ММ.ГГГГ):\n"
        "Например: 15.05.2026",
        reply_markup=ReplyKeyboardMarkup([["⬅️ Назад", "❌ Отмена"]], resize_keyboard=True)
    )
    return DATE


async def choose_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "⬅️ Назад":
        await update.message.reply_text("Выбери услугу:", reply_markup=services_keyboard)
        return SERVICE
    if text == "❌ Отмена":
        await start(update, context)
        return ConversationHandler.END

    context.user_data["date"] = text
    await update.message.reply_text(
        "⏰ Выбери удобное время:",
        reply_markup=time_keyboard
    )
    return TIME


async def choose_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "⬅️ Назад":
        await update.message.reply_text(
            "📅 Напишите дату записи:",
            reply_markup=ReplyKeyboardMarkup([["⬅️ Назад", "❌ Отмена"]], resize_keyboard=True)
        )
        return DATE
    if text == "❌ Отмена":
        await start(update, context)
        return ConversationHandler.END

    context.user_data["time"] = text

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Картой", callback_data="card")],
        [InlineKeyboardButton("💵 Наличными", callback_data="cash")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_time")]
    ])

    await update.message.reply_text(
        "💰 Выберите способ оплаты:",
        reply_markup=keyboard
    )
    return PAYMENT


async def choose_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "back_to_time":
        await query.message.edit_text("⏰ Выбери удобное время:", reply_markup=None)
        await query.message.reply_text(
            "⏰ Выбери удобное время:",
            reply_markup=time_keyboard
        )
        return TIME

    if query.data == "card":
        context.user_data["payment"] = "💳 Картой"
    else:
        context.user_data["payment"] = "💵 Наличными после ремонта"

    await query.message.reply_text(
        "📱 Пожалуйста, отправьте ваш номер телефона:",
        reply_markup=ReplyKeyboardMarkup([["⬅️ Назад", "❌ Отмена"]], resize_keyboard=True)
    )
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # Обработка кнопок Назад и Отмена
    if text == "⬅️ Назад":
        # Возвращаемся к выбору оплаты
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 Картой", callback_data="card")],
            [InlineKeyboardButton("💵 Наличными", callback_data="cash")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_time")]
        ])
        await update.message.reply_text(
            "💰 Выберите способ оплаты:",
            reply_markup=keyboard
        )
        return PAYMENT

    if text == "❌ Отмена":
        context.user_data.clear()
        await update.message.reply_text(
            "❌ Запись отменена.",
            reply_markup=main_keyboard
        )
        return ConversationHandler.END

    # === Основная логика: сохраняем номер и подтверждаем запись ===
    context.user_data["phone"] = text

    # Сохраняем запись в историю пользователя
    booking = {
        "service": context.user_data.get("service"),
        "date": context.user_data.get("date"),
        "time": context.user_data.get("time"),
        "payment": context.user_data.get("payment"),
        "phone": context.user_data["phone"],
        "created_at": datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
    }

    if "bookings" not in context.user_data:
        context.user_data["bookings"] = []
    context.user_data["bookings"].append(booking)

    user = update.message.from_user
    username = f"@{user.username}" if user.username else "без username"

    # Сообщение администратору
    admin_text = (
        "🚗 НОВАЯ ЗАПИСЬ В АВТОСЕРВИС!\n\n"
        f"👤 Клиент: {user.first_name} {user.last_name or ''}\n"
        f"🔗 Username: {username}\n"
        f"📞 Телефон: {context.user_data['phone']}\n\n"
        f"🛠 Услуга: {context.user_data['service']}\n"
        f"📅 Дата: {context.user_data['date']}\n"
        f"⏰ Время: {context.user_data['time']}\n"
        f"💰 Оплата: {context.user_data['payment']}\n"
        f"🕒 Создано: {booking['created_at']}"
    )

    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text)
    except Exception as e:
        print(f"Ошибка отправки админу: {e}")

    # === ПОДТВЕРЖДЕНИЕ КЛИЕНТУ ===
    await update.message.reply_text(
        "✅ <b>Ваша заявка успешно принята!</b>\n\n"
        f"🛠 Услуга: <b>{context.user_data['service']}</b>\n"
        f"📅 Дата: <b>{context.user_data['date']}</b>\n"
        f"⏰ Время: <b>{context.user_data['time']}</b>\n"
        f"💰 Оплата: <b>{context.user_data['payment']}</b>\n\n"
        "Мы свяжемся с вами в ближайшее время для подтверждения записи.\n\n"
        "Вы можете посмотреть все ваши записи через кнопку «📖 Мои записи»",
        parse_mode="HTML",
        reply_markup=main_keyboard
    )

    # Очищаем данные текущей записи
    context.user_data.pop("service", None)
    context.user_data.pop("date", None)
    context.user_data.pop("time", None)
    context.user_data.pop("payment", None)
    context.user_data.pop("phone", None)

    return ConversationHandler.END
    # Сохраняем запись в историю пользователя
    booking = {
        "service": context.user_data["service"],
        "date": context.user_data["date"],
        "time": context.user_data["time"],
        "payment": context.user_data["payment"],
        "phone": context.user_data["phone"],
        "created_at": datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
    }

    if "bookings" not in context.user_data:
        context.user_data["bookings"] = []
    context.user_data["bookings"].append(booking)

    user = update.message.from_user
    username = user.username or "без username"

    # Отправка админу
    admin_text = (
        "🚗 НОВАЯ ЗАПИСЬ!\n\n"
        f"👤 Клиент: {user.first_name}\n"
        f"🔗 @{username}\n"
        f"📞 Телефон: {context.user_data['phone']}\n\n"
        f"🛠 Услуга: {context.user_data['service']}\n"
        f"📅 Дата: {context.user_data['date']}\n"
        f"⏰ Время: {context.user_data['time']}\n"
        f"💰 Оплата: {context.user_data['payment']}\n"
        f"🕒 Создано: {booking['created_at']}"
    )

    await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text)

    # Подтверждение пользователю
    await update.message.reply_text(
        "✅ **Ваша заявка успешно принята!**\n\n"
        f"🛠 Услуга: {context.user_data['service']}\n"
        f"📅 Дата: {context.user_data['date']} в {context.user_data['time']}\n"
        f"💰 Оплата: {context.user_data['payment']}\n\n"
        "Мы свяжемся с вами для подтверждения в ближайшее время.\n\n"
        "Можете посмотреть все ваши записи в разделе «📖 Мои записи»",
        parse_mode="Markdown",
        reply_markup=main_keyboard
    )

    context.user_data.clear()  # очищаем текущую запись
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Запись отменена.", reply_markup=main_keyboard)
    return ConversationHandler.END


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    booking_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^📝 Записаться$"), booking_start)],
        states={
            SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_service)],
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_date)],
            TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_time)],
            PAYMENT: [CallbackQueryHandler(choose_payment)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(booking_handler)
    app.add_handler(MessageHandler(filters.Regex("^📋 Услуги$"), show_services))
    app.add_handler(MessageHandler(filters.Regex("^📞 Контакты$"), contacts))
    app.add_handler(MessageHandler(filters.Regex("^📖 Мои записи$"), show_my_bookings))  # ← Добавлено

    print("Бот успешно запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
