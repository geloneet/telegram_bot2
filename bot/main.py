import os
import logging
import asyncio
import ipaddress
import pytz
from aiohttp import web
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram.error import NetworkError
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# --- Importaciones de tus módulos ---
from handlers.start_handler import start_command
from handlers.id_handler import id_command
from handlers.help_handler import help_command
from handlers.status_handler import status_command
from handlers.sp_handler import get_sp_conversation_handler
from handlers.recargar_handler import recargar_command
from handlers.saldo_handler import saldo_command
from services.db_service import init_db

# ============================
# 📊 LOGGING
# ============================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================
# 🌎 TIMEZONE CONFIG
# ============================
# APScheduler requiere pytz obligatoriamente
# Ajusta "America/Mexico_City" a tu zona horaria si es diferente
tz = pytz.timezone("America/Mexico_City")
# Inicializa un scheduler para que no use el timezone por defecto del sistema
AsyncIOScheduler(timezone=tz)

# ============================
# 🔐 IP VALIDATION
# ============================
# IPs oficiales de Telegram (rango conocido)
# Fuente: https://core.telegram.org/bots/webhooks#the-short-version
TELEGRAM_IP_RANGES = [
    ipaddress.ip_network('149.154.160.0/20'),
    ipaddress.ip_network('91.108.4.0/22'),
]

# IP interna de tu servidor para permitir requests locales (opcional)
SERVER_IP = os.getenv("SERVER_IP", "127.0.0.1")

async def validate_ip(request):
    """Valida que la IP de origen sea Telegram o el propio servidor"""
    peername = request.transport.get_extra_info('peername')
    if peername is None:
        raise web.HTTPForbidden(text="IP no válida")
    ip, _ = peername
    ip_addr = ipaddress.ip_address(ip)

    # Permitir si viene del propio servidor
    if ip == SERVER_IP:
        return

    # Permitir si viene de Telegram
    for net in TELEGRAM_IP_RANGES:
        if ip_addr in net:
            return

    logger.warning(f"❌ Conexión rechazada desde IP no autorizada: {ip}")
    raise web.HTTPForbidden(text="IP no autorizada")

# ============================
# 🤖 MAIN BOT FUNCTION
# ============================
def main():
    # Inicializar DB
    init_db()

    # Leer token desde .env
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN no configurado en el entorno")

    # Inicializar aplicación Telegram
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Registrar comandos
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("id", id_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(get_sp_conversation_handler())
    app.add_handler(CommandHandler("recargar", recargar_command))
    app.add_handler(CommandHandler("saldo", saldo_command))

    logger.info("🤖 Iniciando bot en modo POLLING (BitLaunch)")

    async def run_bot():
        await app.bot.delete_webhook(drop_pending_updates=True)
        await app.initialize()
        await app.start()
        logger.info("✅ Bot iniciado correctamente y esperando comandos...")
        await app.updater.start_polling()
        await asyncio.Event().wait()

    try:
        loop = asyncio.get_event_loop()
        loop.create_task(run_bot())
        loop.run_forever()
    except (RuntimeError, KeyboardInterrupt):
        logger.info("🛑 Finalizando bot...")
    except NetworkError as e:
        logger.error(f"❌ Error de conexión con Telegram: {e}")

# ============================
# 🏁 ENTRY POINT
# ============================
if __name__ == "__main__":
    main()