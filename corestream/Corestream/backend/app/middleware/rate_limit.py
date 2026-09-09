"""
Rate limiting sencillo basado en Redis (plan 3.5).

No se usa slowapi ni ninguna dependencia nueva: un contador de ventana fija
por clave (IP, o IP+email) es suficiente para lo que hace falta aquí —
frenar fuerza bruta contra /auth/login — y Redis ya está disponible en toda
la aplicación.

Antes: 25 intentos de login fallidos consecutivos, todos respondidos con 401,
ninguno bloqueado. Verificado en la auditoría inicial.
"""

from __future__ import annotations

from fastapi import HTTPException, Request, status

from app.redis_client import get_redis

_PREFIX = "corestream:ratelimit:"


async def _hit(key: str, *, max_attempts: int, window_seconds: int) -> None:
    """
    Incrementa el contador de `key` y lanza 429 si supera max_attempts
    dentro de la ventana. INCR + EXPIRE es atómico a efectos prácticos aquí:
    el único caso límite (perder el EXPIRE por un fallo entre medias) deja el
    contador sin caducar hasta el próximo reinicio de Redis, lo que en el
    peor caso es "demasiado estricto", nunca "permite más de la cuenta".
    """
    redis = await get_redis()
    full_key = f"{_PREFIX}{key}"

    count = await redis.incr(full_key)
    if count == 1:
        await redis.expire(full_key, window_seconds)

    if count > max_attempts:
        ttl = await redis.ttl(full_key)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos. Intenta de nuevo más tarde.",
            headers={"Retry-After": str(max(ttl, 1))},
        )


def _client_ip(request: Request) -> str:
    # Sin proxy delante todavía (fase 6): request.client.host es la IP real.
    # Cuando haya Nginx, esto deberá leer X-Forwarded-For — lo señala el plan
    # en la entrega a sistemas (fase 10): uvicorn necesita --forwarded-allow-ips
    # para que X-Forwarded-For sea de fiar y no lo pueda falsear el cliente.
    return request.client.host if request.client else "desconocido"


async def rate_limit_login(request: Request, email: str | None = None) -> None:
    """
    Límite combinado por IP y por cuenta sobre /auth/login.

    Por IP: una IP no puede intentar más de 20 logins/5min contra ninguna
    cuenta (frena el barrido de credenciales contra muchos emails).
    Por cuenta: una cuenta concreta no puede recibir más de 8 intentos/5min
    sin importar desde cuántas IPs distintas (frena el ataque distribuido
    contra una sola cuenta).
    """
    ip = _client_ip(request)
    await _hit(f"login:ip:{ip}", max_attempts=20, window_seconds=300)
    if email:
        await _hit(f"login:email:{email.lower().strip()}", max_attempts=8, window_seconds=300)
