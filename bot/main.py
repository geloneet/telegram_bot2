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

    # --- CONFIGURACIÓN PARA IONOS (Webhook + listener explícito) ---
    import asyncio
    from aiohttp import web

    PORT = int(os.environ.get("PORT", 8080))
    DOMAIN = os.environ.get("DOMAIN", "home-5018860448.app-ionos.space")
    WEBHOOK_URL = f"https://{DOMAIN}/{BOT_TOKEN}"

    async def handle(request):
        return web.Response(text="✅ Bot Telegram activo en IONOS")

    app_web = web.Application()
    app_web.router.add_get("/", handle)  # respuesta para la raíz
    app_web.router.add_post(f"/{BOT_TOKEN}", app.webhook_handler())  # webhook Telegram

    logger.info(f"🚀 Iniciando bot con webhook en {WEBHOOK_URL} ...")

    # Iniciar webhook manualmente con aiohttp
    async def run():
        await app.bot.set_webhook(WEBHOOK_URL)
        runner = web.AppRunner(app_web)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()
        logger.info(f"✅ Servidor webhook escuchando en puerto {PORT}")
        await asyncio.Event().wait()  # mantener en ejecución

    asyncio.run(run())