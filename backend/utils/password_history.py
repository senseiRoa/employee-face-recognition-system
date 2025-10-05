"""
Sistema de historial de contraseñas para prevenir reutilización
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional
from utils.security import get_password_hash as hash_password, verify_password

Base = declarative_base()


class PasswordHistory(Base):
    """
    Modelo para almacenar historial de contraseñas hasheadas
    """

    __tablename__ = "password_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relación con el usuario
    user = relationship("User", back_populates="password_history")


class PasswordHistoryService:
    """
    Servicio para gestionar el historial de contraseñas
    """

    def __init__(self, db_session):
        self.db = db_session

    def add_password_to_history(self, user_id: int, password: str) -> None:
        """
        Añade una contraseña al historial del usuario
        """
        password_hash = hash_password(password)

        history_entry = PasswordHistory(user_id=user_id, password_hash=password_hash)

        self.db.add(history_entry)
        self.db.commit()

        # Mantener solo las últimas N contraseñas
        self._cleanup_old_passwords(user_id)

    def check_password_reuse(self, user_id: int, new_password: str) -> bool:
        """
        Verifica si la nueva contraseña ya fue usada anteriormente
        Retorna True si la contraseña ya fue usada (no permitir)
        """
        from utils.password_policy import PasswordPolicy

        # Obtener las últimas contraseñas del historial
        history_entries = (
            self.db.query(PasswordHistory)
            .filter(PasswordHistory.user_id == user_id)
            .order_by(PasswordHistory.created_at.desc())
            .limit(PasswordPolicy.HISTORY_SIZE)
            .all()
        )

        # Verificar si la nueva contraseña coincide con alguna anterior
        for entry in history_entries:
            if verify_password(new_password, entry.password_hash):
                return True  # Contraseña ya fue usada

        return False  # Contraseña no ha sido usada

    def _cleanup_old_passwords(self, user_id: int) -> None:
        """
        Elimina contraseñas antiguas, manteniendo solo las últimas N
        """
        from utils.password_policy import PasswordPolicy

        # Obtener todas las entradas del usuario ordenadas por fecha
        all_entries = (
            self.db.query(PasswordHistory)
            .filter(PasswordHistory.user_id == user_id)
            .order_by(PasswordHistory.created_at.desc())
            .all()
        )

        # Si hay más entradas que el límite, eliminar las más antiguas
        if len(all_entries) > PasswordPolicy.HISTORY_SIZE:
            entries_to_delete = all_entries[PasswordPolicy.HISTORY_SIZE :]

            for entry in entries_to_delete:
                self.db.delete(entry)

            self.db.commit()

    def get_password_history_count(self, user_id: int) -> int:
        """
        Obtiene el número de contraseñas en el historial del usuario
        """
        return (
            self.db.query(PasswordHistory)
            .filter(PasswordHistory.user_id == user_id)
            .count()
        )

    def clear_user_password_history(self, user_id: int) -> None:
        """
        Elimina todo el historial de contraseñas de un usuario
        (usar con precaución, solo para casos especiales como reset completo)
        """
        self.db.query(PasswordHistory).filter(
            PasswordHistory.user_id == user_id
        ).delete()
        self.db.commit()

    def get_password_age_days(self, user_id: int) -> Optional[int]:
        """
        Obtiene la edad en días de la contraseña más reciente
        """
        latest_entry = (
            self.db.query(PasswordHistory)
            .filter(PasswordHistory.user_id == user_id)
            .order_by(PasswordHistory.created_at.desc())
            .first()
        )

        if latest_entry:
            delta = datetime.utcnow() - latest_entry.created_at
            return delta.days

        return None


def validate_password_history(user_id: int, new_password: str, db_session) -> bool:
    """
    Función helper para validar que una contraseña no esté en el historial
    """
    history_service = PasswordHistoryService(db_session)

    if history_service.check_password_reuse(user_id, new_password):
        from utils.password_policy import PasswordValidationError, PasswordPolicy

        raise PasswordValidationError(
            f"Password has been used recently. Please choose a different password. "
            f"Cannot reuse any of the last {PasswordPolicy.HISTORY_SIZE} passwords.",
            "PASSWORD_REUSE_NOT_ALLOWED",
        )

    return True
