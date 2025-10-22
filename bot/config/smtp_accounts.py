from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env")

SMTP_ACCOUNTS = {
    "vic": {
        "name": "Compra confirmada",
        "user": os.getenv("VIC_USER"),
        "password": os.getenv("VIC_PASS"),
        "server": os.getenv("VIC_SERVER"),
        "port": int(os.getenv("VIC_PORT")),
    },
    "angel": {
        "name": "Confirmación de venta",
        "user": os.getenv("ANGEL_USER"),
        "password": os.getenv("ANGEL_PASS"),
        "server": os.getenv("ANGEL_SERVER"),
        "port": int(os.getenv("ANGEL_PORT")),
    },
    "viva": {
        "name": "Confirmación de compra",
        "user": os.getenv("VIVA_USER"),
        "password": os.getenv("VIVA_PASS"),
        "server": os.getenv("VIVA_SERVER"),
        "port": int(os.getenv("VIVA_PORT")),
    },
}