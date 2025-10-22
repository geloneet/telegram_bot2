# bot/handlers/help_handler.py
from telegram import Update
from telegram.ext import ContextTypes

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra los comandos disponibles"""
    help_text = (
        "🤖 *Comandos disponibles:*\n\n"
        "📌 /start - Inicia el bot\n"
        "📌 /correo - Envia correos\n"
        "🆔 /id - Muestra tu ID de usuario\n"
        "ℹ️ /status - Verifica si el bot está en línea\n"
        "ℹ️ /saldo - Verifica saldo disponible\n"
        "❓ /help - Muestra esta lista de comandos"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")
