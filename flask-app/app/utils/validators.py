"""Validation utilities for user input."""
import re
from typing import Tuple


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password meets security requirements.

    Requirements:
    - Minimum 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 number
    - At least 1 special character (!@#$%^&*(),.?":{}|<>)

    Args:
        password: Password string to validate

    Returns:
        Tuple of (is_valid: bool, message: str)

    Examples:
        >>> validate_password_strength("weak")
        (False, "La contraseña debe tener al menos 8 caracteres.")

        >>> validate_password_strength("Strong123!")
        (True, "Contraseña válida.")
    """
    if not password:
        return False, "La contraseña es requerida."

    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres."

    if len(password) > 128:
        return False, "La contraseña no puede exceder 128 caracteres."

    # Check for uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "La contraseña debe contener al menos una letra mayúscula."

    # Check for lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "La contraseña debe contener al menos una letra minúscula."

    # Check for digit
    if not re.search(r'\d', password):
        return False, "La contraseña debe contener al menos un número."

    # Check for special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "La contraseña debe contener al menos un carácter especial (!@#$%^&*...)."

    return True, "Contraseña válida."


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email format.

    Args:
        email: Email string to validate

    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    if not email:
        return False, "El email es requerido."

    # RFC 5322 simplified regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(pattern, email):
        return False, "Formato de email inválido."

    if len(email) > 254:  # RFC 5321
        return False, "El email es demasiado largo."

    return True, "Email válido."


def validate_name(name: str, field_name: str = "nombre") -> Tuple[bool, str]:
    """
    Validate name (no special characters, no XSS).

    Args:
        name: Name string to validate
        field_name: Field name for error messages

    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    if not name:
        return False, f"El {field_name} es requerido."

    name = name.strip()

    if len(name) < 2:
        return False, f"El {field_name} debe tener al menos 2 caracteres."

    if len(name) > 100:
        return False, f"El {field_name} no puede exceder 100 caracteres."

    # Allow letters, spaces, hyphens, apostrophes, and common accented characters
    pattern = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-\']+$'

    if not re.match(pattern, name):
        return False, f"El {field_name} solo puede contener letras, espacios, guiones y apóstrofes."

    # Check for potential XSS
    dangerous_chars = ['<', '>', '{', '}', '[', ']', '\\', '/', ';']
    if any(char in name for char in dangerous_chars):
        return False, f"El {field_name} contiene caracteres no permitidos."

    return True, f"{field_name.capitalize()} válido."


def validate_phone(phone: str) -> Tuple[bool, str]:
    """
    Validate phone number (international format).

    Args:
        phone: Phone number string to validate

    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    if not phone:
        return True, "Teléfono opcional."  # Phone is optional

    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)

    # Check if it's digits (with optional + at start)
    pattern = r'^\+?\d{7,15}$'

    if not re.match(pattern, cleaned):
        return False, "Formato de teléfono inválido. Use formato internacional (+593999999999) o local."

    return True, "Teléfono válido."


def validate_cedula(cedula: str) -> Tuple[bool, str]:
    """
    Validate Ecuadorian cédula (ID number).

    Args:
        cedula: Cedula string to validate

    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    if not cedula:
        return True, "Cédula opcional."  # Cedula is optional

    # Remove spaces and hyphens
    cleaned = re.sub(r'[\s\-]', '', cedula)

    # Must be 10 digits
    if not re.match(r'^\d{10}$', cleaned):
        return False, "La cédula debe tener 10 dígitos."

    # Validate using modulo 10 algorithm (Ecuadorian cédula validation)
    try:
        # Get province code (first 2 digits)
        province = int(cleaned[:2])
        if province < 1 or province > 24:
            return False, "Código de provincia inválido en cédula."

        # Get third digit (must be < 6 for natural persons)
        third_digit = int(cleaned[2])
        if third_digit > 5:
            return False, "Cédula no corresponde a persona natural."

        # Validate check digit (last digit)
        coefficients = [2, 1, 2, 1, 2, 1, 2, 1, 2]
        total = 0

        for i, coef in enumerate(coefficients):
            value = int(cleaned[i]) * coef
            if value > 9:
                value -= 9
            total += value

        check_digit = (10 - (total % 10)) % 10

        if check_digit != int(cleaned[9]):
            return False, "Dígito verificador de cédula inválido."

        return True, "Cédula válida."

    except (ValueError, IndexError):
        return False, "Formato de cédula inválido."


def validate_address(address: str) -> Tuple[bool, str]:
    """
    Validate address (basic validation).

    Args:
        address: Address string to validate

    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    if not address:
        return False, "La dirección es requerida."

    address = address.strip()

    if len(address) < 10:
        return False, "La dirección debe tener al menos 10 caracteres."

    if len(address) > 500:
        return False, "La dirección no puede exceder 500 caracteres."

    # Check for potential XSS
    dangerous_chars = ['<', '>', '{', '}', '[', ']', '\\', ';']
    if any(char in address for char in dangerous_chars):
        return False, "La dirección contiene caracteres no permitidos."

    return True, "Dirección válida."


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent XSS and SQL injection.

    Args:
        text: Text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized text string
    """
    if not text:
        return ""

    # Strip leading/trailing whitespace
    text = text.strip()

    # Limit length
    if len(text) > max_length:
        text = text[:max_length]

    # Remove null bytes
    text = text.replace('\x00', '')

    # Escape HTML special characters (basic XSS prevention)
    # Note: Flask's Jinja2 templates auto-escape by default, but this adds extra layer
    html_escape_table = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '/': '&#x2F;'
    }

    for char, escaped in html_escape_table.items():
        text = text.replace(char, escaped)

    return text


def validate_price(price, field_name: str = "precio") -> Tuple[bool, str]:
    """
    Validate price value.

    Args:
        price: Price value (float, int, or string)
        field_name: Field name for error messages

    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    if price is None:
        return False, f"El {field_name} es requerido."

    try:
        price_float = float(price)
    except (ValueError, TypeError):
        return False, f"El {field_name} debe ser un número válido."

    if price_float < 0:
        return False, f"El {field_name} no puede ser negativo."

    if price_float > 999999.99:
        return False, f"El {field_name} excede el máximo permitido."

    return True, f"{field_name.capitalize()} válido."


def validate_stock(stock, field_name: str = "stock") -> Tuple[bool, str]:
    """
    Validate stock value.

    Args:
        stock: Stock value (int or string)
        field_name: Field name for error messages

    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    if stock is None:
        return False, f"El {field_name} es requerido."

    try:
        stock_int = int(stock)
    except (ValueError, TypeError):
        return False, f"El {field_name} debe ser un número entero."

    if stock_int < 0:
        return False, f"El {field_name} no puede ser negativo."

    if stock_int > 1000000:
        return False, f"El {field_name} excede el máximo permitido."

    return True, f"{field_name.capitalize()} válido."


def validate_quantity(quantity, max_quantity: int = 100) -> Tuple[bool, str]:
    """
    Validate purchase quantity.

    Args:
        quantity: Quantity value (int or string)
        max_quantity: Maximum allowed quantity per order

    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    if quantity is None:
        return False, "La cantidad es requerida."

    try:
        qty_int = int(quantity)
    except (ValueError, TypeError):
        return False, "La cantidad debe ser un número entero."

    if qty_int < 1:
        return False, "La cantidad debe ser al menos 1."

    if qty_int > max_quantity:
        return False, f"La cantidad máxima por orden es {max_quantity}."

    return True, "Cantidad válida."
