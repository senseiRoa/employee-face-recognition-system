""""""""""""

Endpoints para gestión de contraseñas con validación y seguridad mejorada

"""Endpoints para gestión de contraseñas

from fastapi import APIRouter, Depends, HTTPException, status, Request

from sqlalchemy.orm import Session"""Endpoints para gestión de contraseñasEndpoints para gestión de contraseñas

from typing import Dict, Any

from datetime import datetime, timedeltafrom fastapi import APIRouter, Depends, HTTPException, status, Request

import secrets

from sqlalchemy.orm import Session""""""

from database import get_db

from dependencies import get_current_userfrom typing import Dict, Any

from services.user_service import UserService

from datetime import datetime, timedeltafrom fastapi import APIRouter, Depends, HTTPException, status, Request

router = APIRouter(prefix="/auth", tags=["password"])

import secrets



@router.post("/reset-password-simple")from sqlalchemy.orm import Sessionfrom fastapi import APIRouter, Depends, HTTPException, status, Request

async def reset_password_simple(

    token: str,from database import get_db

    new_password: str,

    db: Session = Depends(get_db)from dependencies import get_current_userfrom typing import Dict, Anyfr        if not user:

):

    """from utils.rate_limiter import RateLimiter

    Resetear contraseña usando token de reset - versión simplificada

    """from utils.password_policy import (from datetime import datetime, timedelta            # Por seguridad, no revelar si el email existe o no

    try:

        user_service = UserService(db)    PasswordValidator, 

        

        # Buscar usuario por token de reset    ChangePasswordRequest, import secrets            # Pero aún así devolver una respuesta consistente

        user = user_service.get_user_by_reset_token(token)

            ResetPasswordRequest,

        if not user:

            raise HTTPException(    PasswordValidationError            return {

                status_code=status.HTTP_400_BAD_REQUEST,

                detail="Invalid or expired reset token")

            )

        from utils.password_history import PasswordHistoryService, validate_password_historyfrom database import get_db                "message": "If the email exists, a password reset link has been sent",

        # Verificar que el token no haya expirado

        if user.reset_token_expires < datetime.utcnow():from utils.security import get_password_hash as hash_password, verify_password

            raise HTTPException(

                status_code=status.HTTP_400_BAD_REQUEST,from services.user_service import UserServicefrom dependencies import get_current_user                "status": "sent",

                detail="Reset token has expired"

            )

        

        # Validar que la nueva contraseña sea fuerterouter = APIRouter(prefix="/auth", tags=["password"])from utils.rate_limiter import RateLimiter                "email": email

        if len(new_password) < 8:

            raise HTTPException(

                status_code=status.HTTP_400_BAD_REQUEST,

                detail="Password must be at least 8 characters long"# Configurar rate limiterfrom utils.password_policy import (            }alchemy.or        # TODO: Aquí se enviaría el email con el token

            )

        rate_limiter = RateLimiter()

        # Actualizar contraseña

        from utils.security import get_password_hash    PasswordValidator,         # Por ahora, devolvemos el token en la respuesta (solo para desarrollo)

        user.password = get_password_hash(new_password)

        user.password_changed_at = datetime.utcnow()

        user.reset_token = None

        user.reset_token_expires = None@router.post("/change-password")    ChangePasswordRequest,         return {

        db.commit()

        async def change_password(

        return {

            "message": "Password has been reset successfully",    request: Request,    ResetPasswordRequest,            "message": "Password reset link has been sent to your email",

            "reset_at": user.password_changed_at.isoformat(),

            "user_id": user.id,    password_data: ChangePasswordRequest,

            "username": user.username,

            "status": "success"    current_user: dict = Depends(get_current_user),    PasswordValidationError            "status": "sent",

        }

            db: Session = Depends(get_db)

    except HTTPException:

        raise):)            "email": email,

    except Exception as e:

        db.rollback()    """

        raise HTTPException(

            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,    Cambiar contraseña del usuario actualfrom utils.password_history import PasswordHistoryService, validate_password_history            "reset_token": reset_token,  # Remover en producción

            detail=f"Error resetting password: {str(e)}"

        )    Requiere autenticación y contraseña actual



    """from utils.security import get_password_hash as hash_password, verify_password            "expires_at": reset_expires.isoformat(),

@router.post("/forgot-password-simple")

async def forgot_password_simple(    # Rate limiting

    email: str,

    db: Session = Depends(get_db)    client_ip = request.client.hostfrom services.user_service import UserService            "valid_for_minutes": 60

):

    """    rate_limiter.check_rate_limit(

    Solicitar reset de contraseña por email - versión simplificada

    """        key=f"password_change_{client_ip}_{current_user['id']}",        } Session

    try:

        user_service = UserService(db)        endpoint="password_change"

        user = user_service.get_user_by_email(email)

            )router = APIRouter(prefix="/auth", tags=["password"])from typing import Dict, Any

        if not user:

            # Por seguridad, no revelar si el email existe    

            return {

                "message": "If the email exists, a password reset link has been sent",    try:from datetime import datetime, timedelta

                "status": "sent",

                "email": email        user_service = UserService(db)

            }

                user = user_service.get_user_by_id(current_user["id"])# Configurar rate limiterimport secrets

        # Generar token de reset

        reset_token = secrets.token_urlsafe(32)        

        reset_expires = datetime.utcnow() + timedelta(hours=1)

                if not user:rate_limiter = RateLimiter()from database import get_db

        # Guardar token

        user.reset_token = reset_token            raise HTTPException(

        user.reset_token_expires = reset_expires

        db.commit()                status_code=status.HTTP_404_NOT_FOUND,from dependencies import get_current_user

        

        return {                detail="User not found"

            "message": "Password reset link has been sent to your email",

            "status": "sent",            )from utils.rate_limiter import RateLimiter

            "email": email,

            "reset_token": reset_token,  # En producción, esto se enviaría por email        

            "expires_at": reset_expires.isoformat(),

            "valid_for_minutes": 60        # Verificar contraseña actual@router.post("/change-password", response_model=Dict[str, str])from utils.password_policy import (

        }

                if not verify_password(password_data.current_password, user.password):

    except Exception as e:

        db.rollback()            raise HTTPException(async def change_password(    PasswordValidator,

        raise HTTPException(

            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,                status_code=status.HTTP_400_BAD_REQUEST,

            detail=f"Error processing password reset: {str(e)}"

        )                detail="Current password is incorrect"    request: Request,    ChangePasswordRequest,



            )

@router.get("/password-test")

async def password_test():            password_data: ChangePasswordRequest,    ResetPasswordRequest,

    """

    Endpoint de prueba para verificar que el módulo funciona        # Validar nueva contraseña con políticas

    """

    return {        try:    current_user: dict = Depends(get_current_user),    PasswordValidationError,

        "message": "Password endpoints are working",

        "available_endpoints": [            PasswordValidator.validate_password(

            "/auth/forgot-password-simple",

            "/auth/reset-password-simple",                password_data.new_password,    db: Session = Depends(get_db))

            "/auth/password-test"

        ]                username=user.username,

    }
                email=user.email):from utils.password_history import PasswordHistoryService, validate_password_history

            )

        except PasswordValidationError as e:    """from utils.security import get_password_hash as hash_password, verify_password

            raise HTTPException(

                status_code=status.HTTP_400_BAD_REQUEST,    Cambiar contraseña del usuario actualfrom services.user_service import UserService

                detail=f"Password validation failed: {e.message}"

            )    Requiere autenticación y contraseña actual

        

        # Verificar historial de contraseñas    """router = APIRouter(prefix="/auth", tags=["password"])

        try:

            validate_password_history(user.id, password_data.new_password, db)    # Rate limiting

        except PasswordValidationError as e:

            raise HTTPException(    client_ip = request.client.host# Configurar rate limiter

                status_code=status.HTTP_400_BAD_REQUEST,

                detail=e.message    rate_limiter.check_rate_limit(rate_limiter = RateLimiter()

            )

                key=f"password_change_{client_ip}_{current_user['id']}",

        # Guardar contraseña anterior en historial antes del cambio

        history_service = PasswordHistoryService(db)        endpoint="password_change"

        history_service.add_password_to_history(user.id, password_data.current_password)

            )@router.post("/change-password", response_model=Dict[str, str])

        # Actualizar contraseña

        user.password = hash_password(password_data.new_password)    async def change_password(

        user.password_changed_at = datetime.utcnow()

        db.commit()    try:    request: Request,

        

        return {        user_service = UserService(db)    password_data: ChangePasswordRequest,

            "message": "Password changed successfully",

            "changed_at": user.password_changed_at.isoformat(),        user = user_service.get_user_by_id(current_user["id"])    current_user: dict = Depends(get_current_user),

            "user_id": user.id,

            "username": user.username,            db: Session = Depends(get_db),

            "status": "success"

        }        if not user:):

        

    except HTTPException:            raise HTTPException(    """

        raise

    except Exception as e:                status_code=status.HTTP_404_NOT_FOUND,    Cambiar contraseña del usuario actual

        db.rollback()

        raise HTTPException(                detail="User not found"    Requiere autenticación y contraseña actual

            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail=f"Error changing password: {str(e)}"            )    """

        )

            # Rate limiting



@router.post("/forgot-password")        # Verificar contraseña actual    client_ip = request.client.host

async def forgot_password(

    request: Request,        if not verify_password(password_data.current_password, user.password):    rate_limiter.check_rate_limit(

    email: str,

    db: Session = Depends(get_db)            raise HTTPException(        key=f"password_change_{client_ip}_{current_user['id']}",

):

    """                status_code=status.HTTP_400_BAD_REQUEST,        endpoint="password_change",

    Solicitar reset de contraseña por email

    """                detail="Current password is incorrect"    )

    # Rate limiting

    client_ip = request.client.host            )

    rate_limiter.check_rate_limit(

        key=f"password_reset_{client_ip}",            try:

        endpoint="password_reset"

    )        # Validar nueva contraseña con políticas        user_service = UserService(db)

    

    try:        try:        user = user_service.get_user_by_id(current_user["id"])

        user_service = UserService(db)

        user = user_service.get_user_by_email(email)            PasswordValidator.validate_password(

        

        if not user:                password_data.new_password,        if not user:

            # Por seguridad, no revelar si el email existe o no

            return {                username=user.username,            raise HTTPException(

                "message": "If the email exists, a password reset link has been sent",

                "status": "sent",                email=user.email                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"

                "email": email,

                "note": "Check your email for reset instructions"            )            )

            }

                except PasswordValidationError as e:

        # Generar token de reset

        reset_token = secrets.token_urlsafe(32)            raise HTTPException(        # Verificar contraseña actual

        reset_expires = datetime.utcnow() + timedelta(hours=1)  # 1 hora de validez

                        status_code=status.HTTP_400_BAD_REQUEST,        if not verify_password(password_data.current_password, user.password):

        # Guardar token en la base de datos

        user.reset_token = reset_token                detail=f"Password validation failed: {e.message}"            raise HTTPException(

        user.reset_token_expires = reset_expires

        db.commit()            )                status_code=status.HTTP_400_BAD_REQUEST,

        

        # TODO: Aquí se enviaría el email con el token                        detail="Current password is incorrect",

        return {

            "message": "Password reset link has been sent to your email",        # Verificar historial de contraseñas            )

            "status": "sent",

            "email": email,        try:

            "reset_token": reset_token,  # Remover en producción

            "expires_at": reset_expires.isoformat(),            validate_password_history(user.id, password_data.new_password, db)        # Validar nueva contraseña con políticas

            "valid_for_minutes": 60,

            "note": "In production, this token would be sent via email"        except PasswordValidationError as e:        try:

        }

                    raise HTTPException(            PasswordValidator.validate_password(

    except Exception as e:

        db.rollback()                status_code=status.HTTP_400_BAD_REQUEST,                password_data.new_password, username=user.username, email=user.email

        raise HTTPException(

            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,                detail=e.message            )

            detail=f"Error processing password reset: {str(e)}"

        )            )        except PasswordValidationError as e:



                    raise HTTPException(

@router.post("/reset-password")

async def reset_password(        # Guardar contraseña anterior en historial antes del cambio                status_code=status.HTTP_400_BAD_REQUEST,

    request: Request,

    reset_data: ResetPasswordRequest,        history_service = PasswordHistoryService(db)                detail=f"Password validation failed: {e.message}",

    db: Session = Depends(get_db)

):        history_service.add_password_to_history(user.id, password_data.current_password)            )

    """

    Resetear contraseña usando token de reset        

    """

    # Rate limiting        # Actualizar contraseña        # Verificar historial de contraseñas

    client_ip = request.client.host

    rate_limiter.check_rate_limit(        user.password = hash_password(password_data.new_password)        try:

        key=f"password_reset_confirm_{client_ip}",

        endpoint="password_reset"        user.password_changed_at = datetime.utcnow()            validate_password_history(user.id, password_data.new_password, db)

    )

            db.commit()        except PasswordValidationError as e:

    try:

        user_service = UserService(db)                    raise HTTPException(

        

        # Buscar usuario por token de reset        return {                status_code=status.HTTP_400_BAD_REQUEST, detail=e.message

        user = user_service.get_user_by_reset_token(reset_data.token)

                    "message": "Password changed successfully",            )

        if not user:

            raise HTTPException(            "changed_at": user.password_changed_at.isoformat(),

                status_code=status.HTTP_400_BAD_REQUEST,

                detail="Invalid or expired reset token"            "user_id": user.id,        # Guardar contraseña anterior en historial antes del cambio

            )

                    "username": user.username        history_service = PasswordHistoryService(db)

        # Verificar que el token no haya expirado

        if user.reset_token_expires < datetime.utcnow():        }        history_service.add_password_to_history(user.id, password_data.current_password)

            raise HTTPException(

                status_code=status.HTTP_400_BAD_REQUEST,        

                detail="Reset token has expired"

            )    except HTTPException:        # Actualizar contraseña

        

        # Validar nueva contraseña        raise        user.password = hash_password(password_data.new_password)

        try:

            PasswordValidator.validate_password(    except Exception as e:        user.password_changed_at = datetime.utcnow()

                reset_data.new_password,

                username=user.username,        db.rollback()        db.commit()

                email=user.email

            )        raise HTTPException(

        except PasswordValidationError as e:

            raise HTTPException(            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,        return {

                status_code=status.HTTP_400_BAD_REQUEST,

                detail=f"Password validation failed: {e.message}"            detail=f"Error changing password: {str(e)}"            "message": "Password changed successfully",

            )

                )            "changed_at": user.password_changed_at.isoformat(),

        # Verificar historial (opcional en reset)

        try:        }

            validate_password_history(user.id, reset_data.new_password, db)

        except PasswordValidationError as e:

            raise HTTPException(

                status_code=status.HTTP_400_BAD_REQUEST,@router.post("/forgot-password", response_model=Dict[str, str])    except HTTPException:

                detail=e.message

            )async def forgot_password(        raise

        

        # Guardar contraseña anterior en historial antes del cambio    request: Request,    except Exception as e:

        if user.password:  # Solo si ya tenía contraseña

            from utils.password_history import PasswordHistory    email: str,        db.rollback()

            history_entry = PasswordHistory(

                user_id=user.id,    db: Session = Depends(get_db)        raise HTTPException(

                password_hash=user.password

            )):            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

            db.add(history_entry)

            """            detail=f"Error changing password: {str(e)}",

        # Actualizar contraseña y limpiar token

        user.password = hash_password(reset_data.new_password)    Solicitar reset de contraseña por email        )

        user.password_changed_at = datetime.utcnow()

        user.reset_token = None    """

        user.reset_token_expires = None

        db.commit()    # Rate limiting

        

        return {    client_ip = request.client.host@router.post("/forgot-password", response_model=Dict[str, str])

            "message": "Password has been reset successfully",

            "reset_at": user.password_changed_at.isoformat(),    rate_limiter.check_rate_limit(async def forgot_password(request: Request, email: str, db: Session = Depends(get_db)):

            "user_id": user.id,

            "username": user.username,        key=f"password_reset_{client_ip}",    """

            "status": "success"

        }        endpoint="password_reset"    Solicitar reset de contraseña por email

        

    except HTTPException:    )    """

        raise

    except Exception as e:        # Rate limiting

        db.rollback()

        raise HTTPException(    try:    client_ip = request.client.host

            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail=f"Error resetting password: {str(e)}"        user_service = UserService(db)    rate_limiter.check_rate_limit(

        )

        user = user_service.get_user_by_email(email)        key=f"password_reset_{client_ip}", endpoint="password_reset"



@router.get("/password-requirements")            )

async def get_password_requirements():

    """        if not user:

    Obtener los requisitos de contraseña del sistema

    """            # Por seguridad, no revelar si el email existe o no    try:

    requirements = PasswordValidator.generate_password_requirements()

    return {            # Pero aún así devolver una respuesta consistente        user_service = UserService(db)

        "message": "Password requirements for the system",

        "requirements": requirements,            return {        user = user_service.get_user_by_email(email)

        "examples": {

            "valid": ["MySecure123!", "StrongP@ss2024", "Complex!Pass9"],                "message": "If the email exists, a password reset link has been sent",

            "invalid": ["password", "123456", "short", "NODIGITS!"]

        }                "status": "sent",        if not user:

    }

                "email": email,            # Por seguridad, no revelar si el email existe o no



@router.post("/check-password-strength")                "note": "Check your email for reset instructions"            return {

async def check_password_strength(password: str):

    """            }                "message": "If the email exists, a password reset link has been sent",

    Evaluar la fortaleza de una contraseña

    """                        "status": "sent",

    try:

        strength_info = PasswordValidator.get_password_strength(password)        # Generar token de reset            }

        errors = PasswordValidator.get_validation_errors(password)

                reset_token = secrets.token_urlsafe(32)

        return {

            "strength": strength_info,        reset_expires = datetime.utcnow() + timedelta(hours=1)  # 1 hora de validez        # Generar token de reset

            "meets_requirements": len(errors) == 0,

            "error_count": len(errors),                reset_token = secrets.token_urlsafe(32)

            "errors": errors if len(errors) <= 5 else errors[:5],

            "recommendations": [        # Guardar token en la base de datos        reset_expires = datetime.utcnow() + timedelta(hours=1)  # 1 hora de validez

                "Use a mix of uppercase and lowercase letters",

                "Include numbers and special characters",        user.reset_token = reset_token

                "Avoid common patterns and dictionary words",

                "Make it at least 8 characters long"        user.reset_token_expires = reset_expires        # Guardar token en la base de datos

            ]

        }        db.commit()        user.reset_token = reset_token

        

    except Exception as e:                user.reset_token_expires = reset_expires

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,        # TODO: Aquí se enviaría el email con el token        db.commit()

            detail=f"Error checking password strength: {str(e)}"

        )        # Por ahora, devolvemos el token en la respuesta (solo para desarrollo)



        return {        # TODO: Aquí se enviaría el email con el token

@router.get("/password-history-info")

async def get_password_history_info(            "message": "Password reset link has been sent to your email",        # Por ahora, devolvemos el token en la respuesta (solo para desarrollo)

    current_user: dict = Depends(get_current_user),

    db: Session = Depends(get_db)            "status": "sent",        return {

):

    """            "email": email,            "message": "Password reset link has been sent to your email",

    Obtener información del historial de contraseñas del usuario actual

    """            "reset_token": reset_token,  # Remover en producción            "status": "sent",

    try:

        history_service = PasswordHistoryService(db)            "expires_at": reset_expires.isoformat(),            "reset_token": reset_token,  # Remover en producción

        

        history_count = history_service.get_password_history_count(current_user["id"])            "valid_for_minutes": 60,            "expires_at": reset_expires.isoformat(),

        password_age = history_service.get_password_age_days(current_user["id"])

                    "note": "In production, this token would be sent via email"        }

        from utils.password_policy import PasswordPolicy

                }

        return {

            "user_id": current_user["id"],            except Exception as e:

            "username": current_user["username"],

            "password_history_count": history_count,    except Exception as e:        db.rollback()

            "password_age_days": password_age,

            "last_changed": "N/A" if password_age is None else f"{password_age} days ago",        db.rollback()        raise HTTPException(

            "max_history_size": PasswordPolicy.HISTORY_SIZE,

            "security_status": "good" if password_age and password_age < 90 else "consider_change",        raise HTTPException(            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

            "recommendations": {

                "change_frequency": "Every 90 days",            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,            detail=f"Error processing password reset: {str(e)}",

                "avoid_reuse": f"Last {PasswordPolicy.HISTORY_SIZE} passwords",

                "strength_tips": "Use strong, unique passwords"            detail=f"Error processing password reset: {str(e)}"        )

            }

        }        )

        

    except Exception as e:

        raise HTTPException(

            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,@router.post("/reset-password", response_model=Dict[str, str])

            detail=f"Error getting password history info: {str(e)}"

        )@router.post("/reset-password", response_model=Dict[str, str])async def reset_password(

async def reset_password(    request: Request, reset_data: ResetPasswordRequest, db: Session = Depends(get_db)

    request: Request,):

    reset_data: ResetPasswordRequest,    """

    db: Session = Depends(get_db)    Resetear contraseña usando token de reset

):    """

    """    # Rate limiting

    Resetear contraseña usando token de reset    client_ip = request.client.host

    """    rate_limiter.check_rate_limit(

    # Rate limiting        key=f"password_reset_confirm_{client_ip}", endpoint="password_reset"

    client_ip = request.client.host    )

    rate_limiter.check_rate_limit(

        key=f"password_reset_confirm_{client_ip}",    try:

        endpoint="password_reset"        user_service = UserService(db)

    )

            # Buscar usuario por token de reset

    try:        user = user_service.get_user_by_reset_token(reset_data.token)

        user_service = UserService(db)

                if not user:

        # Buscar usuario por token de reset            raise HTTPException(

        user = user_service.get_user_by_reset_token(reset_data.token)                status_code=status.HTTP_400_BAD_REQUEST,

                        detail="Invalid or expired reset token",

        if not user:            )

            raise HTTPException(

                status_code=status.HTTP_400_BAD_REQUEST,        # Verificar que el token no haya expirado

                detail="Invalid or expired reset token"        if user.reset_token_expires < datetime.utcnow():

            )            raise HTTPException(

                        status_code=status.HTTP_400_BAD_REQUEST,

        # Verificar que el token no haya expirado                detail="Reset token has expired",

        if user.reset_token_expires < datetime.utcnow():            )

            raise HTTPException(

                status_code=status.HTTP_400_BAD_REQUEST,        # Validar nueva contraseña

                detail="Reset token has expired"        try:

            )            PasswordValidator.validate_password(

                        reset_data.new_password, username=user.username, email=user.email

        # Validar nueva contraseña            )

        try:        except PasswordValidationError as e:

            PasswordValidator.validate_password(            raise HTTPException(

                reset_data.new_password,                status_code=status.HTTP_400_BAD_REQUEST,

                username=user.username,                detail=f"Password validation failed: {e.message}",

                email=user.email            )

            )

        except PasswordValidationError as e:        # Verificar historial (opcional en reset, se puede comentar si se desea permitir)

            raise HTTPException(        try:

                status_code=status.HTTP_400_BAD_REQUEST,            validate_password_history(user.id, reset_data.new_password, db)

                detail=f"Password validation failed: {e.message}"        except PasswordValidationError as e:

            )            raise HTTPException(

                        status_code=status.HTTP_400_BAD_REQUEST, detail=e.message

        # Verificar historial (opcional en reset, se puede comentar si se desea permitir)            )

        try:

            validate_password_history(user.id, reset_data.new_password, db)        # Guardar contraseña anterior en historial antes del cambio

        except PasswordValidationError as e:        if user.password:  # Solo si ya tenía contraseña

            raise HTTPException(            history_service = PasswordHistoryService(db)

                status_code=status.HTTP_400_BAD_REQUEST,            # Como no tenemos la contraseña en texto plano, guardamos el hash actual

                detail=e.message            # Este es un caso especial donde guardamos el hash directamente

            )            from utils.password_history import PasswordHistory

        

        # Guardar contraseña anterior en historial antes del cambio            history_entry = PasswordHistory(

        if user.password:  # Solo si ya tenía contraseña                user_id=user.id, password_hash=user.password

            # Como no tenemos la contraseña en texto plano, guardamos el hash actual            )

            # Este es un caso especial donde guardamos el hash directamente            db.add(history_entry)

            from utils.password_history import PasswordHistory

            history_entry = PasswordHistory(        # Actualizar contraseña y limpiar token

                user_id=user.id,        user.password = hash_password(reset_data.new_password)

                password_hash=user.password        user.password_changed_at = datetime.utcnow()

            )        user.reset_token = None

            db.add(history_entry)        user.reset_token_expires = None

                db.commit()

        # Actualizar contraseña y limpiar token

        user.password = hash_password(reset_data.new_password)        return {

        user.password_changed_at = datetime.utcnow()            "message": "Password has been reset successfully",

        user.reset_token = None            "reset_at": user.password_changed_at.isoformat(),

        user.reset_token_expires = None        }

        db.commit()

            except HTTPException:

        return {        raise

            "message": "Password has been reset successfully",    except Exception as e:

            "reset_at": user.password_changed_at.isoformat(),        db.rollback()

            "user_id": user.id,        raise HTTPException(

            "username": user.username,            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

            "status": "success"            detail=f"Error resetting password: {str(e)}",

        }        )

        

    except HTTPException:

        raise@router.get("/password-requirements", response_model=Dict[str, Any])

    except Exception as e:async def get_password_requirements():

        db.rollback()    """

        raise HTTPException(    Obtener los requisitos de contraseña del sistema

            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,    """

            detail=f"Error resetting password: {str(e)}"    return {

        )        "requirements": PasswordValidator.generate_password_requirements(),

        "message": "Password requirements for the system",

    }

@router.get("/password-requirements", response_model=Dict[str, Any])

async def get_password_requirements():

    """@router.post("/check-password-strength", response_model=Dict[str, Any])

    Obtener los requisitos de contraseña del sistemaasync def check_password_strength(password: str):

    """    """

    requirements = PasswordValidator.generate_password_requirements()    Evaluar la fortaleza de una contraseña

    return {    """

        "message": "Password requirements for the system",    try:

        "requirements": requirements,        strength_info = PasswordValidator.get_password_strength(password)

        "examples": {

            "valid": ["MySecure123!", "StrongP@ss2024", "Complex!Pass9"],        # No revelar errores específicos para evitar información sensible

            "invalid": ["password", "123456", "short", "NODIGITS!"]        errors = PasswordValidator.get_validation_errors(password)

        }

    }        return {

            "strength": strength_info,

            "meets_requirements": len(errors) == 0,

@router.post("/check-password-strength", response_model=Dict[str, Any])            "error_count": len(errors),

async def check_password_strength(password: str):            "errors": errors

    """            if len(errors) <= 5

    Evaluar la fortaleza de una contraseña            else errors[:5],  # Limitar errores mostrados

    """        }

    try:

        strength_info = PasswordValidator.get_password_strength(password)    except Exception as e:

                raise HTTPException(

        # No revelar errores específicos para evitar información sensible            status_code=status.HTTP_400_BAD_REQUEST,

        errors = PasswordValidator.get_validation_errors(password)            detail=f"Error checking password strength: {str(e)}",

                )

        return {

            "strength": strength_info,

            "meets_requirements": len(errors) == 0,@router.get("/password-history-info")

            "error_count": len(errors),async def get_password_history_info(

            "errors": errors if len(errors) <= 5 else errors[:5],  # Limitar errores mostrados    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)

            "recommendations": [):

                "Use a mix of uppercase and lowercase letters",    """

                "Include numbers and special characters",    Obtener información del historial de contraseñas del usuario actual

                "Avoid common patterns and dictionary words",    """

                "Make it at least 8 characters long"    try:

            ]        history_service = PasswordHistoryService(db)

        }

                history_count = history_service.get_password_history_count(current_user["id"])

    except Exception as e:        password_age = history_service.get_password_age_days(current_user["id"])

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,        return {

            detail=f"Error checking password strength: {str(e)}"            "user_id": current_user["id"],

        )            "password_history_count": history_count,

            "password_age_days": password_age,

            "last_changed": "N/A"

@router.get("/password-history-info")            if password_age is None

async def get_password_history_info(            else f"{password_age} days ago",

    current_user: dict = Depends(get_current_user),        }

    db: Session = Depends(get_db)

):    except Exception as e:

    """        raise HTTPException(

    Obtener información del historial de contraseñas del usuario actual            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

    """            detail=f"Error getting password history info: {str(e)}",

    try:        )

        history_service = PasswordHistoryService(db)
        
        history_count = history_service.get_password_history_count(current_user["id"])
        password_age = history_service.get_password_age_days(current_user["id"])
        
        from utils.password_policy import PasswordPolicy
        
        return {
            "user_id": current_user["id"],
            "username": current_user["username"],
            "password_history_count": history_count,
            "password_age_days": password_age,
            "last_changed": "N/A" if password_age is None else f"{password_age} days ago",
            "max_history_size": PasswordPolicy.HISTORY_SIZE,
            "security_status": "good" if password_age and password_age < 90 else "consider_change",
            "recommendations": {
                "change_frequency": "Every 90 days",
                "avoid_reuse": f"Last {PasswordPolicy.HISTORY_SIZE} passwords",
                "strength_tips": "Use strong, unique passwords"
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting password history info: {str(e)}"
        )