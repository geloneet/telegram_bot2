# bot/handlers/recargar_handler.py
from telegram import Update
from telegram.ext import ContextTypes
from services.db_service import add_user_if_not_exists, add_credits, get_credits
from telegram.error import Forbidden, BadRequest

MASTER_ID = 5941956756  # Usuario maestro

async def recargar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caller_id = update.effective_user.id

    if caller_id != MASTER_ID:
        await update.message.reply_text("⛔ No tienes permiso para usar este comando.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Uso: /recargar <id_usuario> <cantidad>")
        return

    try:
        target_id = int(context.args[0])
        cantidad = int(context.args[1])
        assert cantidad > 0
    except Exception:
        await update.message.reply_text("❌ Argumentos inválidos. Ejemplo: /recargar 123456789 5")
        return

    add_user_if_not_exists(target_id)
    add_credits(target_id, cantidad)
    total = get_credits(target_id)

    # Confirma al maestro
    await update.message.reply_text(
        f"✅ Recargados {cantidad} créditos a {target_id}. Saldo actual: {total}"
    )

    # Notifica al usuario objetivo (si ya habló con el bot)
    try:
        await context.bot.send_message(
            chat_id=target_id,
            text=f"💳 Se te han agregado *{cantidad}* créditos. Saldo actual: *{total}*.",
            parse_mode="Markdown"
        )
    except (Forbidden, BadRequest) as e:
        # Ocurre cuando el usuario NUNCA inició chat con el bot, o bloqueó el bot.
        await update.message.reply_text(
            "⚠️ No pude notificar al usuario (no ha iniciado chat con el bot o bloqueó al bot)."
        )