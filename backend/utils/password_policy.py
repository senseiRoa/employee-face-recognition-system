"""
Validador de políticas de contraseña estrictas
Implementa reglas de seguridad para contraseñas fuertes
"""

import re
from typing import List
from pydantic import BaseModel, validator


class PasswordPolicy:
    """
    Configuración de políticas de contraseña
    """

    MIN_LENGTH = 8
    MAX_LENGTH = 128
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGITS = True
    REQUIRE_SPECIAL_CHARS = True
    MIN_SPECIAL_CHARS = 1
    FORBIDDEN_PATTERNS = [
        "password",
        "123456",
        "qwerty",
        "abc123",
        "admin",
        "user",
        "welcome",
        "login",
        "pass",
        "root",
        "test",
        "guest",
    ]
    MAX_REPEATED_CHARS = 3
    HISTORY_SIZE = 5  # Número de contraseñas anteriores a recordar


class PasswordValidationError(Exception):
    """Excepción personalizada para errores de validación de contraseña"""

    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class PasswordValidator:
    """
    Validador de políticas de contraseña
    """

    @staticmethod
    def validate_password(
        password: str, username: str = None, email: str = None
    ) -> bool:
        """
        Valida una contraseña contra todas las políticas
        Lanza PasswordValidationError si no cumple los requisitos
        """
        errors = PasswordValidator.get_validation_errors(password, username, email)

        if errors:
            raise PasswordValidationError(
                f"Password does not meet requirements: {', '.join(errors)}",
                "PASSWORD_POLICY_VIOLATION",
            )

        return True

    @staticmethod
    def get_validation_errors(
        password: str, username: str = None, email: str = None
    ) -> List[str]:
        """
        Obtiene una lista de errores de validación para una contraseña
        """
        errors = []

        # Verificar longitud mínima
        if len(password) < PasswordPolicy.MIN_LENGTH:
            errors.append(
                f"must be at least {PasswordPolicy.MIN_LENGTH} characters long"
            )

        # Verificar longitud máxima
        if len(password) > PasswordPolicy.MAX_LENGTH:
            errors.append(f"must not exceed {PasswordPolicy.MAX_LENGTH} characters")

        # Verificar mayúsculas
        if PasswordPolicy.REQUIRE_UPPERCASE and not re.search(r"[A-Z]", password):
            errors.append("must contain at least one uppercase letter")

        # Verificar minúsculas
        if PasswordPolicy.REQUIRE_LOWERCASE and not re.search(r"[a-z]", password):
            errors.append("must contain at least one lowercase letter")

        # Verificar dígitos
        if PasswordPolicy.REQUIRE_DIGITS and not re.search(r"\d", password):
            errors.append("must contain at least one digit")

        # Verificar caracteres especiales
        if PasswordPolicy.REQUIRE_SPECIAL_CHARS:
            special_chars = re.findall(
                r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password
            )
            if len(special_chars) < PasswordPolicy.MIN_SPECIAL_CHARS:
                errors.append(
                    f"must contain at least {PasswordPolicy.MIN_SPECIAL_CHARS} special character(s)"
                )

        # Verificar patrones prohibidos
        password_lower = password.lower()
        for pattern in PasswordPolicy.FORBIDDEN_PATTERNS:
            if pattern in password_lower:
                errors.append(f"must not contain common patterns like '{pattern}'")

        # Verificar caracteres repetidos
        if PasswordValidator._has_excessive_repeated_chars(password):
            errors.append(
                f"must not have more than {PasswordPolicy.MAX_REPEATED_CHARS} consecutive repeated characters"
            )

        # Verificar que no contenga username o email
        if username and username.lower() in password_lower:
            errors.append("must not contain the username")

        if email:
            email_parts = email.lower().split("@")
            if email_parts[0] in password_lower:
                errors.append("must not contain the email address")

        return errors

    @staticmethod
    def _has_excessive_repeated_chars(password: str) -> bool:
        """Verifica si hay demasiados caracteres repetidos consecutivos"""
        count = 1
        for i in range(1, len(password)):
            if password[i] == password[i - 1]:
                count += 1
                if count > PasswordPolicy.MAX_REPEATED_CHARS:
                    return True
            else:
                count = 1
        return False

    @staticmethod
    def generate_password_requirements() -> dict:
        """
        Genera un diccionario con los requisitos de contraseña para mostrar al usuario
        """
        return {
            "min_length": PasswordPolicy.MIN_LENGTH,
            "max_length": PasswordPolicy.MAX_LENGTH,
            "requires_uppercase": PasswordPolicy.REQUIRE_UPPERCASE,
            "requires_lowercase": PasswordPolicy.REQUIRE_LOWERCASE,
            "requires_digits": PasswordPolicy.REQUIRE_DIGITS,
            "requires_special_chars": PasswordPolicy.REQUIRE_SPECIAL_CHARS,
            "min_special_chars": PasswordPolicy.MIN_SPECIAL_CHARS,
            "max_repeated_chars": PasswordPolicy.MAX_REPEATED_CHARS,
            "forbidden_patterns": PasswordPolicy.FORBIDDEN_PATTERNS,
        }

    @staticmethod
    def get_password_strength(password: str) -> dict:
        """
        Evalúa la fortaleza de una contraseña y retorna un score
        """
        score = 0
        feedback = []

        # Longitud (0-25 puntos)
        length_score = min(25, (len(password) / PasswordPolicy.MIN_LENGTH) * 10)
        score += length_score

        # Diversidad de caracteres (0-25 puntos)
        char_types = 0
        if re.search(r"[a-z]", password):
            char_types += 1
        if re.search(r"[A-Z]", password):
            char_types += 1
        if re.search(r"\d", password):
            char_types += 1
        if re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
            char_types += 1

        diversity_score = (char_types / 4) * 25
        score += diversity_score

        # Complejidad (0-25 puntos)
        complexity_score = 0
        if (
            len(set(password)) / len(password) > 0.7
        ):  # Alta diversidad de caracteres únicos
            complexity_score += 10
        if not PasswordValidator._has_excessive_repeated_chars(password):
            complexity_score += 10
        if len(password) >= 12:
            complexity_score += 5

        score += complexity_score

        # Ausencia de patrones comunes (0-25 puntos)
        pattern_score = 25
        password_lower = password.lower()
        for pattern in PasswordPolicy.FORBIDDEN_PATTERNS:
            if pattern in password_lower:
                pattern_score -= 5

        score += max(0, pattern_score)

        # Determinar nivel de fortaleza
        if score >= 80:
            strength = "Very Strong"
            color = "green"
        elif score >= 60:
            strength = "Strong"
            color = "lightgreen"
        elif score >= 40:
            strength = "Medium"
            color = "orange"
        elif score >= 20:
            strength = "Weak"
            color = "red"
        else:
            strength = "Very Weak"
            color = "darkred"

        return {
            "score": int(score),
            "strength": strength,
            "color": color,
            "feedback": feedback,
        }


class PasswordPolicyValidator:
    """Validador de Pydantic para usar en modelos"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: str, values: dict = None) -> str:
        """Validador para usar con Pydantic"""
        username = values.get("username") if values else None
        email = values.get("email") if values else None

        PasswordValidator.validate_password(value, username, email)
        return value


# Modelo Pydantic para cambio de contraseña
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

    @validator("new_password")
    def validate_new_password(cls, v, values):
        username = values.get("username")
        email = values.get("email")
        PasswordValidator.validate_password(v, username, email)
        return v

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("passwords do not match")
        return v


# Modelo para reset de contraseña
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str

    @validator("new_password")
    def validate_new_password(cls, v):
        PasswordValidator.validate_password(v)
        return v

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("passwords do not match")
        return v
