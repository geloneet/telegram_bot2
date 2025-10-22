from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters
)
from services.email_service import send_sp_email
from services.db_service import add_user_if_not_exists, deduct_credit, get_credits
from utils.validators import is_valid_email
from config.smtp_accounts import SMTP_ACCOUNTS
import asyncio
import logging
import threading

# Configurar logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

ASK_SUBJECT, ASK_SMTP = range(2)
user_pending_data = {}

async def correo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    add_user_if_not_exists(user_id)

    if not context.args:
        await update.message.reply_text("Uso correcto: /correo <correo_destino>")
        return ConversationHandler.END

    to_email = context.args[0].strip()

    if not is_valid_email(to_email):
        await update.message.reply_text("❌ El correo no es válido. Ejemplo: /correo usuario@dominio.com")
        return ConversationHandler.END

    current_credits = get_credits(user_id)
    if current_credits <= 0:
        await update.message.reply_text("❌ No tienes créditos suficientes. Usa /saldo para consultar tus créditos.")
        return ConversationHandler.END

    user_pending_data[user_id] = {"to": to_email}
    await update.message.reply_text(
        f"📨 Dime el *asunto* que quieres poner en el correo para {to_email}:",
        parse_mode="Markdown"
    )
    return ASK_SUBJECT

async def handle_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    subject = update.message.text
    if user_id not in user_pending_data:
        await update.message.reply_text("⚠️ No se encontró un correo asociado. Usa /correo <correo> primero.")
        return ConversationHandler.END

    user_pending_data[user_id]["subject"] = subject

    # Crear botones
    keyboard = [
        [
            InlineKeyboardButton("📧 Gate 1", callback_data="vic"),
            InlineKeyboardButton("📧 Gate 2", callback_data="angel"),
            InlineKeyboardButton("📧 Gate 3", callback_data="viva")
    ],
    [
        InlineKeyboardButton("❌ Cancelar", callback_data="cancelar_sp")
    ]
]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("📮 Elige desde qué correo quieres enviar: \n Gate 1 - Recomendado para Hotmail \n Gate 2 - Recomendado para Gmail \n Gate 3 - Recomendado para Empresariales ", reply_markup=reply_markup)
    return ASK_SMTP

async def send_emails(user_id, to_emails, base_subject, smtp_info, context):
    for to_email in to_emails:
        success = send_sp_email([to_email], base_subject, smtp_info)
        if not success:
            break
        await asyncio.sleep(6)  # Espera 6 segundos antes de enviar el siguiente correo

    if success:
        deduct_credit(user_id, 1)  # Descontar 1 crédito por el comando /correo
        remaining = get_credits(user_id)
        await context.bot.send_message(
            chat_id=user_id,
            text=f"✅ Correos enviados con éxito.\n💰 Te quedan {remaining} créditos."
        )
    else:
        await context.bot.send_message(
            chat_id=user_id,
            text="⚠️ Error al enviar los correos. No se ha descontado ningún crédito."
        )

    user_pending_data.pop(user_id, None)

def send_emails_in_thread(user_id, to_emails, base_subject, smtp_info, context):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(send_emails(user_id, to_emails, base_subject, smtp_info, context))
    except Exception as e:
        logger.error(f"Error en el hilo de envío de correos: {e}")
    finally:
        loop.close()

async def handle_smtp_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    choice = query.data

    # 🔹 Si el usuario presiona "Cancelar"
    if choice == "cancelar_sp":
        await query.edit_message_text("❌ Envío cancelado por el usuario.")
        user_pending_data.pop(user_id, None)
        return ConversationHandler.END

    # 🔹 Continuar con el flujo normal
    if user_id not in user_pending_data or choice not in SMTP_ACCOUNTS:
        await query.edit_message_text("⚠️ Error: No se encontró el flujo o el correo seleccionado no es válido.")
        return ConversationHandler.END

    data = user_pending_data[user_id]
    smtp_info = SMTP_ACCOUNTS[choice]
    base_email = data["to"]
    base_subject = data["subject"]

    # Genera las direcciones de correo electrónico modificadas
    to_emails = [f"{base_email.split('@')[0]}+{i}@{base_email.split('@')[1]}" for i in range(1, 81)]

    await query.edit_message_text(f"📤 Enviando correos ...")

    # Ejecutar el envío de correos en un hilo separado
    threading.Thread(target=send_emails_in_thread, args=(user_id, to_emails, base_subject, smtp_info, context)).start()

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_pending_data.pop(user_id, None)
    await update.message.reply_text("❌ Envío cancelado.")
    return ConversationHandler.END

def get_sp_conversation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("correo", correo_command)],
        states={
            ASK_SUBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_subject)],
            ASK_SMTP: [CallbackQueryHandler(handle_smtp_selection)],
        },
        fallbacks=[CommandHandler("cancelar", cancel)],
    )