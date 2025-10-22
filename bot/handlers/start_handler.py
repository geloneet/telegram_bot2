from telegram import Update
from telegram.ext import ContextTypes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde al comando /start"""
    user = update.effective_user
    name = user.first_name if user else "usuario"
    await update.message.reply_text(f"👋 ¡Hola {name}! bienvenido usa /help para ver los comandos disponibles")