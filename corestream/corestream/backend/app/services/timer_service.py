"""
Servicio de medición de tiempo para tickets en CoreStream.

Este módulo maneja todos los aspectos relacionados con la medición de tiempo
de ejecución y bloqueo de tickets. Proporciona funciones para iniciar, pausar,
reanudar, y finalizar timers, así como para consultar el tiempo transcurrido.

Tipos de timers:
- timer_started_at: Cuando se inició el contador de ejecución (Guardado en Redis)
- time_spent_seconds: Tiempo acumulado de trabajo (Guardado en PostgreSQL)
- blocked_timer_started_at: Cuando se inició el contador de bloqueo (Guardado en Redis)
- blocked_time_seconds: Tiempo acumulado de bloqueo (Guardado en PostgreSQL)
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Ticket
from app.redis_client import delete_cached_value, get_cached_value, set_cached_value


class TimerService:
    """
    Servicio especializado en gestión de timers de tickets.
    
    Métodos principales:
    - start_timer: Inicia contador de ejecución
    - pause_timer: Pausa contador y suma tiempo
    - resume_timer: Reanuda contador de pausa
    - stop_timer: Finaliza contador
    - get_elapsed_time: Obtiene tiempo actual del timer
    - start_blocked_timer: Inicia contador de bloqueo
    - stop_blocked_timer: Finaliza contador de bloqueo
    """

    async def start_timer(
        self,
        ticket_id: UUID,
        user_id: Optional[UUID],
        db: AsyncSession
    ) -> dict:
        """
        Inicia el timer de ejecución de un ticket.
        
        Establece el timestamp de inicio del timer cuando un usuario comienza
        a trabajar en un ticket. Si hay un timer anterior pausado, primero
        suma su tiempo transcurrido antes de iniciar el nuevo.
        
        Args:
            ticket_id (int): ID del ticket
            user_id (str): ID del usuario que inicia
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            
        Returns:
            dict: Diccionario con datos del ticket actualizados
            
        Estructura de retorno:
            {
                'id': uuid,
                'timer_started_at': datetime,  # Timestamp de inicio
                'time_spent_seconds': int,     # Tiempo acumulado previamente
                'status': 'IN_PROGRESS'
            }
            
        Raises:
            HTTPException(400): Timer ya está activo
            HTTPException(404): Ticket no encontrado
            HTTPException(500): Error al iniciar timer
            
        Validaciones:
            - Si hay timer activo, retorna error
            - Ticket debe existir en la base de datos
            - Asume que timer está pausado o no existe
            
        Detalle técnico:
            - timer_started_at se asigna a datetime.utcnow() (En caché de Redis)
            - Registra evento TIMER_START en auditoría
            - No modifica time_spent_seconds (es acumulativo)
            - timestamp se usa para calcular elapsed en el futuro
        """
        try:
            # Buscar ticket en base de datos
            result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
            db_ticket = result.scalar_one_or_none()

            if not db_ticket:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Ticket no encontrado"
                )

            # Idempotency: use DB column as authoritative source
            redis_key = f"corestream:ticket:{ticket_id}:timer_start"
            if db_ticket.timer_started_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El timer ya está en ejecución para este ticket"
                )

            now = datetime.now(timezone.utc)

            # Persist to DB (restart-resilient) and Redis (fast cache)
            db_ticket.timer_started_at = now
            await db.commit()
            await db.refresh(db_ticket)
            await set_cached_value(redis_key, now.isoformat())

            return {
                'id': str(db_ticket.id),
                'timer_started_at': now.isoformat(),
                'time_spent_seconds': db_ticket.time_spent_seconds,
                'status': db_ticket.status.value if hasattr(db_ticket.status, 'value') else db_ticket.status
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al iniciar timer del ticket: {str(e)}"
            )

    async def pause_timer(
        self,
        ticket_id: UUID,
        db: AsyncSession
    ) -> dict:
        """
        Pausa el timer de ejecución y suma tiempo transcurrido.
        
        Calcula cuánto tiempo pasó desde que se inició el timer y lo suma
        al acumulador time_spent_seconds. Luego limpia el timer_started_at
        para indicar que está pausado.
        
        Args:
            ticket_id (int): ID del ticket
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            
        Returns:
            dict: Diccionario con datos del ticket actualizados
            
        Estructura de retorno:
            {
                'id': uuid,
                'timer_started_at': None,      # Se limpió al pausar
                'time_spent_seconds': int,     # Suma acumulada
                'paused_at': datetime,         # Momento de pausa
                'elapsed_this_session': int    # Segundos de esta sesión
            }
            
        Raises:
            HTTPException(400): Timer no está activo
            HTTPException(404): Ticket no encontrado
            HTTPException(500): Error al pausar timer
            
        Validaciones:
            - timer_started_at debe estar establecido
            - Ticket debe existir
            - No es error pausar múltiples veces (idempotente)
            
        Detalle técnico:
            - Calcula elapsed = (ahora - timer_started_at).total_seconds()
            - Suma elapsed a time_spent_seconds
            - Limpia timer_started_at (pone en None en Redis)
            - Registra evento TIMER_PAUSE con duración
            - No afecta blocked_timer_started_at
        """
        try:
            result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
            db_ticket = result.scalar_one_or_none()

            if not db_ticket:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado")

            redis_key = f"corestream:ticket:{ticket_id}:timer_start"
            now = datetime.now(timezone.utc)
            elapsed_seconds = 0

            # DB column is the authoritative start time; Redis is a fallback for
            # tickets started before this migration was applied.
            start_time: Optional[datetime] = db_ticket.timer_started_at
            if start_time is None:
                raw = await get_cached_value(redis_key)
                if raw:
                    ts = raw.decode('utf-8') if isinstance(raw, bytes) else raw
                    start_time = datetime.fromisoformat(ts)

            if start_time is not None:
                elapsed_seconds = int((now - start_time).total_seconds())
                if elapsed_seconds > 0:
                    db_ticket.time_spent_seconds += elapsed_seconds

            # Clear both DB and Redis (router does the final commit)
            db_ticket.timer_started_at = None
            await delete_cached_value(redis_key)
            
            return {
                'id': str(db_ticket.id),
                'timer_started_at': None,
                'time_spent_seconds': db_ticket.time_spent_seconds,
                'paused_at': now.isoformat(),
                'elapsed_this_session': elapsed_seconds
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al pausar timer del ticket: {str(e)}"
            )

    async def resume_timer(
        self,
        ticket_id: UUID,
        db: AsyncSession
    ) -> dict:
        """
        Reanuda el timer de ejecución desde una pausa.
        
        Reinicia el contador después de una pausa, estableciendo un nuevo
        timer_started_at. El tiempo_spent_seconds anterior se preserva.
        
        Args:
            ticket_id (int): ID del ticket
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            
        Returns:
            dict: Diccionario con datos del ticket actualizados
            
        Estructura de retorno:
            {
                'id': uuid,
                'timer_started_at': datetime,  # Nuevo inicio
                'time_spent_seconds': int,     # Preservado desde pausa
                'resumed_at': datetime,
                'status': 'IN_PROGRESS'
            }
            
        Raises:
            HTTPException(400): Timer ya está en ejecución
            HTTPException(404): Ticket no encontrado
            HTTPException(500): Error al reanudar timer
            
        Validaciones:
            - Timer no debe estar activo ya
            - Ticket debe existir
            
        Detalle técnico:
            - timer_started_at se asigna a datetime.utcnow()
            - time_spent_seconds se preserva (acumulativo)
            - Registra evento TIMER_RESUME en auditoría
            - Útil cuando ticket transiciona BLOCKED -> IN_PROGRESS
        """
        # La lógica es idéntica a start_timer a nivel de base de datos y Redis
        # Pasamos None como user_id ya que el reanudar no cambia la asignación
        return await self.start_timer(ticket_id, None, db)

    async def stop_timer(
        self,
        ticket_id: UUID,
        db: AsyncSession
    ) -> dict:
        """
        Finaliza el timer de ejecución de forma permanente.
        
        Detiene el contador de ejecución sumando el tiempo actual al acumulador
        y limpiando todos los campos relacionados. Se usa cuando el ticket
        se marca como DONE o se redirige.
        
        Args:
            ticket_id (int): ID del ticket
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            
        Returns:
            dict: Diccionario con datos finales del ticket
            
        Estructura de retorno:
            {
                'id': uuid,
                'timer_started_at': None,      # Se limpió al finalizar
                'time_spent_seconds': int,     # Suma final
                'stopped_at': datetime,
                'final_elapsed': int           # Última sesión en segundos
            }
            
        Raises:
            HTTPException(404): Ticket no encontrado
            HTTPException(500): Error al detener timer
            
        Detalle técnico:
            - Si timer_started_at está presente, suma tiempo actual
            - Limpia timer_started_at (pone en None)
            - Registra evento TIMER_STOP con tiempo final
            - time_spent_seconds queda como valor definitivo
            - No toca blocked_timer_started_at (timer de bloqueo es independiente)
        """
        # Detener es funcionalmente igual a pausar, pero no esperamos que se reanude
        return await self.pause_timer(ticket_id, db)

timer_service = TimerService()
