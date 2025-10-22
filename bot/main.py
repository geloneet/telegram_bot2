import logging
from telegram.ext import ApplicationBuilder, CommandHandler
from config.config import BOT_TOKEN

# Importar handlers
from handlers.start_handler import start_command
from handlers.id_handler import id_command
from handlers.help_handler import help_command
from handlers.status_handler import status_command
from handlers.sp_handler import get_sp_conversation_handler
from services.db_service import add_user_if_not_exists, deduct_credit, get_credits
from services.db_service import init_db
from handlers.recargar_handler import recargar_command
from handlers.recargar_handler import recargar_command
from handlers.saldo_handler import saldo_command


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    init_db()
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
    app.add_handler(CommandHandler("recargar", recargar_command))
    app.add_handler(CommandHandler("saldo", saldo_command))
    

    logger.info("Bot iniciado correctamente y esperando comandos...")
    app.run_polling()

if __name__ == "__main__":
    main()