"""
Rate limiting middleware para endpoints de autenticación
Implementa límites de intentos de login y registro para prevenir ataques
"""

import time
import asyncio
from collections import defaultdict, deque
from typing import Dict, Deque, Tuple
from fastapi import HTTPException, Request, status
from datetime import datetime, timedelta


class RateLimiter:
    """
    Implementación de rate limiting con ventana deslizante
    """

    def __init__(self):
        # Estructura: {ip_address: deque([(timestamp, endpoint), ...])}
        self.requests: Dict[str, Deque[Tuple[float, str]]] = defaultdict(deque)

        # Configuración de límites por endpoint
        self.limits = {
            "/auth/login": {
                "max_requests": 5,
                "window_seconds": 300,
            },  # 5 intentos en 5 minutos
            "/auth/register": {
                "max_requests": 3,
                "window_seconds": 600,
            },  # 3 registros en 10 minutos
            "/auth/forgot-password": {
                "max_requests": 3,
                "window_seconds": 900,
            },  # 3 resets en 15 minutos
            "/auth/change-password": {
                "max_requests": 5,
                "window_seconds": 300,
            },  # 5 cambios en 5 minutos
        }

    def is_allowed(self, client_ip: str, endpoint: str) -> bool:
        """
        Verifica si la request está permitida según los límites
        """
        if endpoint not in self.limits:
            return True

        current_time = time.time()
        limit_config = self.limits[endpoint]
        window_seconds = limit_config["window_seconds"]
        max_requests = limit_config["max_requests"]

        # Limpiar requests antiguos
        client_requests = self.requests[client_ip]
        while client_requests and client_requests[0][0] < current_time - window_seconds:
            client_requests.popleft()

        # Contar requests para este endpoint en la ventana
        endpoint_requests = sum(
            1 for _, req_endpoint in client_requests if req_endpoint == endpoint
        )

        if endpoint_requests >= max_requests:
            return False

        # Agregar la request actual
        client_requests.append((current_time, endpoint))
        return True

    def get_reset_time(self, client_ip: str, endpoint: str) -> int:
        """
        Obtiene el tiempo en segundos hasta que se resetee el límite
        """
        if endpoint not in self.limits:
            return 0

        current_time = time.time()
        limit_config = self.limits[endpoint]
        window_seconds = limit_config["window_seconds"]

        client_requests = self.requests[client_ip]
        if not client_requests:
            return 0

        # Encontrar la request más antigua para este endpoint
        oldest_request = None
        for timestamp, req_endpoint in client_requests:
            if req_endpoint == endpoint:
                oldest_request = timestamp
                break

        if oldest_request is None:
            return 0

        reset_time = oldest_request + window_seconds - current_time
        return max(0, int(reset_time))


# Instancia global del rate limiter
rate_limiter = RateLimiter()


def check_rate_limit(request: Request, endpoint: str):
    """
    Middleware function para verificar rate limits
    """
    client_ip = request.client.host if request.client else "unknown"

    if not rate_limiter.is_allowed(client_ip, endpoint):
        reset_time = rate_limiter.get_reset_time(client_ip, endpoint)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Too many requests",
                "message": f"Rate limit exceeded for {endpoint}",
                "retry_after": reset_time,
                "endpoint": endpoint,
            },
            headers={"Retry-After": str(reset_time)},
        )


def auth_rate_limit(request: Request):
    """Rate limit específico para endpoints de autenticación"""
    endpoint = request.url.path
    check_rate_limit(request, endpoint)


def get_client_ip(request: Request) -> str:
    """Obtiene la IP del cliente considerando proxies"""
    # Verificar headers de proxy
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    return request.client.host if request.client else "unknown"
