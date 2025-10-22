# bot/handlers/status_handler.py
from telegram import Update
from telegram.ext import ContextTypes

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verifica si el bot está en línea"""
    await update.message.reply_text("✅ El bot está en línea y funcionando correctamente.")