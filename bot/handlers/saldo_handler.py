# bot/handlers/saldo_handler.py
from telegram import Update
from telegram.ext import ContextTypes
from services.db_service import add_user_if_not_exists, get_credits

async def saldo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user_if_not_exists(user.id)
    credits = get_credits(user.id)
    await update.message.reply_text(f"💰 Tu saldo actual es: {credits} créditos.")