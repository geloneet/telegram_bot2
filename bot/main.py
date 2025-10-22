def main():
    import asyncio
    from telegram.ext import ApplicationBuilder, CommandHandler
    from telegram.error import NetworkError

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

    # --- DETECTAR ENTORNO (IONOS o local) ---
    domain = os.getenv("DOMAIN", "")
    is_ionos = "ionos.space" in domain

    async def run_bot():
        if is_ionos:
            # En IONOS — usar POLLING porque el proxy bloquea webhooks (403)
            logger.info("🌐 Ejecutando en IONOS: usando modo POLLING (sin webhook)")
            await app.bot.delete_webhook(drop_pending_updates=True)
            await app.run_polling()
        else:
            # Local o VPS — usar webhook si se define un dominio
            from aiohttp import web
            PORT = int(os.getenv("PORT", 8080))
            DOMAIN = domain or "localhost"
            WEBHOOK_URL = f"https://{DOMAIN}/{BOT_TOKEN}"

            logger.info(f"🚀 Iniciando bot con webhook en {WEBHOOK_URL} ...")
            await app.bot.set_webhook(WEBHOOK_URL)

            app_web = web.Application()
            app_web.router.add_get("/", lambda r: web.Response(text="✅ Bot activo"))
            app_web.router.add_post(f"/{BOT_TOKEN}", app.webhook_request_handler)

            runner = web.AppRunner(app_web)
            await runner.setup()
            site = web.TCPSite(runner, "0.0.0.0", PORT)
            await site.start()

            logger.info(f"✅ Servidor webhook escuchando en puerto {PORT}")
            await asyncio.Event().wait()

    try:
        asyncio.run(run_bot())
    except NetworkError as e:
        logger.error(f"❌ Error de conexión con Telegram: {e}")
        logger.info("Reintentando en 5 segundos...")
        import time
        time.sleep(5)
        asyncio.run(run_bot())


if __name__ == "__main__":
    main()