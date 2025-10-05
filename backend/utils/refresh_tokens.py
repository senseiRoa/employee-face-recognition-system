"""
Sistema de Refresh Tokens para sesiones prolongadas
Maneja tokens de acceso de corta duración y tokens de refresh de larga duración
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from database import Base
from models import User
from utils.jwt_handler import create_access_token, decode_token


class RefreshToken(Base):
    """
    Modelo para almacenar refresh tokens en la base de datos
    """

    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    device_info = Column(String(500), nullable=True)  # User agent, etc.


class RefreshTokenService:
    """
    Servicio para manejar refresh tokens
    """

    REFRESH_TOKEN_EXPIRE_DAYS = 30  # 30 días de duración
    ACCESS_TOKEN_EXPIRE_MINUTES = 15  # 15 minutos de duración

    @staticmethod
    def generate_refresh_token() -> str:
        """Genera un refresh token seguro"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def create_refresh_token(
        db: Session, user_id: int, device_info: Optional[str] = None
    ) -> RefreshToken:
        """
        Crea un nuevo refresh token para el usuario
        """
        # Revocar tokens existentes para el mismo dispositivo (opcional)
        # RefreshTokenService.revoke_user_tokens(db, user_id, device_info)

        token = RefreshTokenService.generate_refresh_token()
        expires_at = datetime.utcnow() + timedelta(
            days=RefreshTokenService.REFRESH_TOKEN_EXPIRE_DAYS
        )

        refresh_token = RefreshToken(
            user_id=user_id, token=token, expires_at=expires_at, device_info=device_info
        )

        db.add(refresh_token)
        db.commit()
        db.refresh(refresh_token)

        return refresh_token

    @staticmethod
    def validate_refresh_token(db: Session, token: str) -> Optional[RefreshToken]:
        """
        Valida un refresh token y retorna el objeto si es válido
        """
        refresh_token = (
            db.query(RefreshToken)
            .filter(
                RefreshToken.token == token,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > datetime.utcnow(),
            )
            .first()
        )

        if refresh_token:
            # Actualizar last_used
            refresh_token.last_used = datetime.utcnow()
            db.commit()

        return refresh_token

    @staticmethod
    def revoke_refresh_token(db: Session, token: str) -> bool:
        """
        Revoca un refresh token específico
        """
        refresh_token = (
            db.query(RefreshToken).filter(RefreshToken.token == token).first()
        )

        if refresh_token:
            refresh_token.is_revoked = True
            db.commit()
            return True

        return False

    @staticmethod
    def revoke_user_tokens(
        db: Session, user_id: int, device_info: Optional[str] = None
    ) -> int:
        """
        Revoca todos los refresh tokens de un usuario
        Si device_info se proporciona, solo revoca tokens de ese dispositivo
        """
        query = db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id, RefreshToken.is_revoked == False
        )

        if device_info:
            query = query.filter(RefreshToken.device_info == device_info)

        count = query.count()
        query.update({"is_revoked": True})
        db.commit()

        return count

    @staticmethod
    def cleanup_expired_tokens(db: Session) -> int:
        """
        Limpia tokens expirados de la base de datos
        """
        count = (
            db.query(RefreshToken)
            .filter(RefreshToken.expires_at < datetime.utcnow())
            .count()
        )

        db.query(RefreshToken).filter(
            RefreshToken.expires_at < datetime.utcnow()
        ).delete()

        db.commit()
        return count

    @staticmethod
    def create_token_pair(
        db: Session, user: User, device_info: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Crea un par de access token y refresh token
        """
        # Crear access token
        access_token_expires = timedelta(
            minutes=RefreshTokenService.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = create_access_token(
            data={
                "sub": user.username,
                "user_id": user.id,
                "company_id": user.company_id,
                "role": user.role.name,
            },
            expires_delta=access_token_expires,
        )

        # Crear refresh token
        refresh_token_obj = RefreshTokenService.create_refresh_token(
            db, user.id, device_info
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token_obj.token,
            "token_type": "bearer",
            "expires_in": RefreshTokenService.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "refresh_expires_in": RefreshTokenService.REFRESH_TOKEN_EXPIRE_DAYS
            * 24
            * 60
            * 60,
        }

    @staticmethod
    def refresh_access_token(
        db: Session, refresh_token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Genera un nuevo access token usando el refresh token
        """
        # Validar refresh token
        token_obj = RefreshTokenService.validate_refresh_token(db, refresh_token)
        if not token_obj:
            return None

        # Obtener usuario
        user = db.query(User).filter(User.id == token_obj.user_id).first()
        if not user or not user.is_active:
            return None

        # Crear nuevo access token
        access_token_expires = timedelta(
            minutes=RefreshTokenService.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = create_access_token(
            data={
                "sub": user.username,
                "user_id": user.id,
                "company_id": user.company_id,
                "role": user.role.name,
            },
            expires_delta=access_token_expires,
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": RefreshTokenService.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    @staticmethod
    def get_user_active_sessions(db: Session, user_id: int) -> list:
        """
        Obtiene todas las sesiones activas de un usuario
        """
        sessions = (
            db.query(RefreshToken)
            .filter(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > datetime.utcnow(),
            )
            .order_by(RefreshToken.last_used.desc())
            .all()
        )

        return [
            {
                "token_id": session.id,
                "device_info": session.device_info,
                "created_at": session.created_at,
                "last_used": session.last_used,
                "expires_at": session.expires_at,
            }
            for session in sessions
        ]
