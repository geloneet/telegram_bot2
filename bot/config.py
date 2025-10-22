# bot/config.py
import os
from dotenv import load_dotenv

# Cargar variables del archivo .env (ubicado en la carpeta bot)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# Leer token del entorno
BOT_TOKEN = os.getenv("BOT_TOKEN")