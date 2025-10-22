# bot/handlers/id_handler.py
from telegram import Update
from telegram.ext import ContextTypes

async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde con el ID del usuario"""
    user = update.effective_user
    if user:
        await update.message.reply_text(f"🆔 Tu ID de usuario es: {user.id}")
    else:
        await update.message.reply_text("No se pudo obtener tu ID de usuario.")