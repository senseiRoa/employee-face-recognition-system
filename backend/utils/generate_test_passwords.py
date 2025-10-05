"""
Script para generar contraseñas fuertes para tests y datos iniciales
"""

from utils.password_policy import PasswordValidator
from utils.security import get_password_hash
import secrets
import string


def generate_strong_password(length=12):
    """Genera una contraseña fuerte que cumple todas las políticas"""
    # Asegurar que tenga al menos uno de cada tipo
    password = ""

    # Al menos una mayúscula
    password += secrets.choice(string.ascii_uppercase)

    # Al menos una minúscula
    password += secrets.choice(string.ascii_lowercase)

    # Al menos un dígito
    password += secrets.choice(string.digits)

    # Al menos un carácter especial
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    password += secrets.choice(special_chars)

    # Completar el resto de la longitud
    all_chars = string.ascii_letters + string.digits + special_chars
    for _ in range(length - 4):
        password += secrets.choice(all_chars)

    # Mezclar los caracteres
    password_list = list(password)
    secrets.SystemRandom().shuffle(password_list)
    password = "".join(password_list)

    return password


# Generar contraseñas específicas para roles
def get_test_passwords():
    """Devuelve contraseñas fuertes para tests"""
    return {
        "admin": "SystemHead2024!",  # Para usuario admin
        "manager": "OfficeChief2024#",  # Para usuario manager
        "employee": "StaffMember2024$",  # Para usuario employee
        "temp": "TempAccess123!",  # Para usuarios temporales en tests
    }


def get_hashed_test_passwords():
    """Devuelve contraseñas hasheadas para tests"""
    passwords = get_test_passwords()
    return {role: get_password_hash(pwd) for role, pwd in passwords.items()}


if __name__ == "__main__":
    # Probar las contraseñas generadas
    passwords = get_test_passwords()

    print("🔐 Contraseñas Fuertes Generadas para Tests:")
    print("=" * 50)

    for role, password in passwords.items():
        try:
            PasswordValidator.validate_password(password)
            strength = PasswordValidator.get_password_strength(password)
            print(
                f"✅ {role:10}: {password:15} (Score: {strength['score']}/100 - {strength['strength']})"
            )
        except Exception as e:
            print(f"❌ {role:10}: {password:15} - ERROR: {e}")

    print("\n🔒 Hashes para usar en la base de datos:")
    print("=" * 50)
    hashed = get_hashed_test_passwords()
    for role, hash_val in hashed.items():
        print(f"{role}: {hash_val[:50]}...")
