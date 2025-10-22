import os
import logging
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram.error import NetworkError

# --- Importaciones de tus módulos ---
from handlers.start_handler import start_command
from handlers.id_handler import id_command
from handlers.help_handler import help_command
from handlers.status_handler import status_command
from handlers.sp_handler import get_sp_conversation_handler
from handlers.recargar_handler import recargar_command
from handlers.saldo_handler import saldo_command
from services.db_service import init_db  # ✅ importante

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    init_db()

    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN no configurado en el entorno")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Registrar comandos
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("id", id_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(get_sp_conversation_handler())
    app.add_handler(CommandHandler("recargar", recargar_command))
    app.add_handler(CommandHandler("saldo", saldo_command))

    logger.info("🤖 Iniciando bot...")

    # --- Forzar modo POLLING en IONOS ---
    domain = os.getenv("DOMAIN", "")
    is_ionos = True  # fuerza modo polling

    async def run_bot():
        logger.info("🌐 Ejecutando en IONOS: usando modo POLLING (sin webhook)")
        await app.bot.delete_webhook(drop_pending_updates=True)
        await app.run_polling()

    try:
        try:
            loop = asyncio.get_running_loop()
            logger.info("🔁 Usando loop existente (IONOS / Actions)")
            loop.create_task(run_bot())
            loop.run_forever()
        except RuntimeError:
            logger.info("🆕 Creando nuevo loop local")
            asyncio.run(run_bot())
    except NetworkError as e:
        logger.error(f"❌ Error de conexión con Telegram: {e}")
        logger.info("Reintentando en 5 segundos...")
        import time
        time.sleep(5)
        asyncio.run(run_bot())


if __name__ == "__main__":
    main()