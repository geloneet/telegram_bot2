from dotenv import load_dotenv
import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler
from config.config import BOT_TOKEN

# Importar handlers
from handlers.start_handler import start_command
from handlers.id_handler import id_command
from handlers.help_handler import help_command
from handlers.status_handler import status_command
from handlers.sp_handler import get_sp_conversation_handler
from services.db_service import add_user_if_not_exists, deduct_credit, get_credits, init_db
from handlers.recargar_handler import recargar_command
from handlers.saldo_handler import saldo_command

# Cargar variables del archivo .env
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Inicializar base de datos
    init_db()

    # Obtener token del entorno
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN no configurado en el entorno")

    # Crear la aplicación del bot
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Registrar handlers y comandos
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("id", id_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(get_sp_conversation_handler())
    app.add_handler(CommandHandler("recargar", recargar_command))
    app.add_handler(CommandHandler("saldo", saldo_command))

    # --- CONFIGURACIÓN PARA IONOS (MODO WEBHOOK) ---
    PORT = int(os.environ.get("PORT", 8080))
    DOMAIN = os.environ.get("DOMAIN", "home-5018860448.app-ionos.space")  # dominio IONOS
    WEBHOOK_URL = f"https://{DOMAIN}/{BOT_TOKEN}"

    logger.info(f"🚀 Iniciando bot con webhook en {WEBHOOK_URL} ...")

    # Iniciar webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    main()