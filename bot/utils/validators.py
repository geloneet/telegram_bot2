# bot/utils/validators.py
import re

def is_valid_email(email: str) -> bool:
    """
    Verifica si un correo tiene un formato válido.
    """
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None