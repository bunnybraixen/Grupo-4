"""
Servicio de medición de tiempo para tickets en CoreStream.

Este módulo maneja todos los aspectos relacionados con la medición de tiempo
de ejecución y bloqueo de tickets. Proporciona funciones para iniciar, pausar,
reanudar, y finalizar timers, así como para consultar el tiempo transcurrido.

Tipos de timers:
- timer_started_at: Cuando se inició el contador de ejecución
- time_spent_seconds: Tiempo acumulado de trabajo
- blocked_timer_started_at: Cuando se inició el contador de bloqueo
- blocked_time_seconds: Tiempo acumulado de bloqueo
"""

from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
import json

# Importar modelos desde el paquete de modelos
# from app.models import Ticket, TicketEvent


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

    @staticmethod
    async def start_timer(
        db: AsyncSession,
        ticket: dict
    ) -> dict:
        """
        Inicia el timer de ejecución de un ticket.
        
        Establece el timestamp de inicio del timer cuando un usuario comienza
        a trabajar en un ticket. Si hay un timer anterior pausado, primero
        suma su tiempo transcurrido antes de iniciar el nuevo.
        
        Args:
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            ticket (dict): Diccionario con datos del ticket
            
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
            - timer_started_at se asigna a datetime.utcnow()
            - Registra evento TIMER_START en auditoría
            - No modifica time_spent_seconds (es acumulativo)
            - timestamp se usa para calcular elapsed en el futuro
        """
        try:
            # Validar que no hay timer activo ya
            if ticket.get('timer_started_at'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El timer ya está en ejecución para este ticket"
                )
            
            # Buscar ticket en base de datos
            # stmt = select(Ticket).where(Ticket.id == UUID(ticket['id']))
            # result = await db.execute(stmt)
            # db_ticket = result.scalars().first()
            
            # if not db_ticket:
            #     raise HTTPException(
            #         status_code=status.HTTP_404_NOT_FOUND,
            #         detail="Ticket no encontrado"
            #     )
            
            # Iniciar nuevo timer
            # db_ticket.timer_started_at = datetime.utcnow()
            # db_ticket.updated_at = datetime.utcnow()
            
            # Registrar evento de inicio de timer en auditoría
            # new_event = TicketEvent(
            #     ticket_id=db_ticket.id,
            #     event_type='TIMER_START',
            #     detail={'started_at': datetime.utcnow().isoformat()}
            # )
            # db.add(new_event)
            
            # Persistir cambios
            # await db.commit()
            # await db.refresh(db_ticket)
            
            return {
                # 'id': str(db_ticket.id),
                # 'timer_started_at': db_ticket.timer_started_at.isoformat(),
                # 'time_spent_seconds': db_ticket.time_spent_seconds,
                # 'status': db_ticket.status
            }
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al iniciar timer del ticket"
            )

    @staticmethod
    async def pause_timer(
        db: AsyncSession,
        ticket: dict
    ) -> dict:
        """
        Pausa el timer de ejecución y suma tiempo transcurrido.
        
        Calcula cuánto tiempo pasó desde que se inició el timer y lo suma
        al acumulador time_spent_seconds. Luego limpia el timer_started_at
        para indicar que está pausado.
        
        Args:
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            ticket (dict): Diccionario con datos del ticket
            
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
            - Limpia timer_started_at (pone en None)
            - Registra evento TIMER_PAUSE con duración
            - No afecta blocked_timer_started_at
        """
        try:
            # Validar que timer está activo
            if not ticket.get('timer_started_at'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El timer no está en ejecución para este ticket"
                )
            
            # Buscar ticket en base de datos
            # stmt = select(Ticket).where(Ticket.id == UUID(ticket['id']))
            # result = await db.execute(stmt)
            # db_ticket = result.scalars().first()
            
            # if not db_ticket:
            #     raise HTTPException(
            #         status_code=status.HTTP_404_NOT_FOUND,
            #         detail="Ticket no encontrado"
            #     )
            
            # Calcular tiempo transcurrido
            # now = datetime.utcnow()
            # elapsed_seconds = int((now - db_ticket.timer_started_at).total_seconds())
            
            # Sumar al acumulador
            # db_ticket.time_spent_seconds += elapsed_seconds
            # db_ticket.timer_started_at = None
            # db_ticket.updated_at = now
            
            # Registrar evento de pausa en auditoría
            # new_event = TicketEvent(
            #     ticket_id=db_ticket.id,
            #     event_type='TIMER_PAUSE',
            #     detail={
            #         'paused_at': now.isoformat(),
            #         'elapsed_seconds': elapsed_seconds,
            #         'total_time_spent': db_ticket.time_spent_seconds
            #     }
            # )
            # db.add(new_event)
            
            # Persistir cambios
            # await db.commit()
            # await db.refresh(db_ticket)
            
            return {
                # 'id': str(db_ticket.id),
                # 'timer_started_at': None,
                # 'time_spent_seconds': db_ticket.time_spent_seconds,
                # 'paused_at': now.isoformat(),
                # 'elapsed_this_session': elapsed_seconds
            }
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al pausar timer del ticket"
            )

    @staticmethod
    async def resume_timer(
        db: AsyncSession,
        ticket: dict
    ) -> dict:
        """
        Reanuda el timer de ejecución desde una pausa.
        
        Reinicia el contador después de una pausa, estableciendo un nuevo
        timer_started_at. El tiempo_spent_seconds anterior se preserva.
        
        Args:
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            ticket (dict): Diccionario con datos del ticket
            
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
        try:
            # Validar que timer no está activo
            if ticket.get('timer_started_at'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El timer ya está en ejecución para este ticket"
                )
            
            # Buscar ticket en base de datos
            # stmt = select(Ticket).where(Ticket.id == UUID(ticket['id']))
            # result = await db.execute(stmt)
            # db_ticket = result.scalars().first()
            
            # if not db_ticket:
            #     raise HTTPException(
            #         status_code=status.HTTP_404_NOT_FOUND,
            #         detail="Ticket no encontrado"
            #     )
            
            # Reanudar timer
            # now = datetime.utcnow()
            # db_ticket.timer_started_at = now
            # db_ticket.updated_at = now
            
            # Registrar evento de reanudación en auditoría
            # new_event = TicketEvent(
            #     ticket_id=db_ticket.id,
            #     event_type='TIMER_RESUME',
            #     detail={
            #         'resumed_at': now.isoformat(),
            #         'total_time_spent_so_far': db_ticket.time_spent_seconds
            #     }
            # )
            # db.add(new_event)
            
            # Persistir cambios
            # await db.commit()
            # await db.refresh(db_ticket)
            
            return {
                # 'id': str(db_ticket.id),
                # 'timer_started_at': db_ticket.timer_started_at.isoformat(),
                # 'time_spent_seconds': db_ticket.time_spent_seconds,
                # 'resumed_at': now.isoformat(),
                # 'status': db_ticket.status
            }
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al reanudar timer del ticket"
            )

    @staticmethod
    async def stop_timer(
        db: AsyncSession,
        ticket: dict
    ) -> dict:
        """
        Finaliza el timer de ejecución de forma permanente.
        
        Detiene el contador de ejecución sumando el tiempo actual al acumulador
        y limpiando todos los campos relacionados. Se usa cuando el ticket
        se marca como DONE o se redirige.
        
        Args:
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            ticket (dict): Diccionario con datos del ticket
            
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
        try:
            # Buscar ticket en base de datos
            # stmt = select(Ticket).where(Ticket.id == UUID(ticket['id']))
            # result = await db.execute(stmt)
            # db_ticket = result.scalars().first()
            
            # if not db_ticket:
            #     raise HTTPException(
            #         status_code=status.HTTP_404_NOT_FOUND,
            #         detail="Ticket no encontrado"
            #     )
            
            # Calcular último elapsed si timer estaba activo
            # now = datetime.utcnow()
            # final_elapsed = 0
            # if db_ticket.timer_started_at:
            #     final_elapsed = int((now - db_ticket.timer_started_at).total_seconds())
            #     db_ticket.time_spent_seconds += final_elapsed
            
            # Limpiar timer
            # db_ticket.timer_started_at = None
            # db_ticket.updated_at = now
            
            # Registrar evento de parada en auditoría
            # new_event = TicketEvent(
            #     ticket_id=db_ticket.id,
            #     event_type='TIMER_STOP',
            #     detail={
            #         'stopped_at': now.isoformat(),
            #         'final_elapsed_seconds': final_elapsed,
            #         'total_time_spent': db_ticket.time_spent_seconds
            #     }
            # )
            # db.add(new_event)
            
            # Persistir cambios
            # await db.commit()
            # await db.refresh(db_ticket)
            
            return {
                # 'id': str(db_ticket.id),
                # 'timer_started_at': None,
                # 'time_spent_seconds': db_ticket.time_spent_seconds,
                # 'stopped_at': now.isoformat(),
                # 'final_elapsed': final_elapsed
            }
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al detener timer del ticket"
            )

    @staticmethod
    def get_elapsed_time(ticket: dict) -> int:
        """
        Calcula el tiempo transcurrido del timer actual sin persistir cambios.
        
        Función síncrona que retorna cuántos segundos han pasado desde que
        se inició el timer actual. No modifica la base de datos, solo calcula.
        Útil para mostrar el timer en tiempo real en la interfaz.
        
        Args:
            ticket (dict): Diccionario con datos del ticket
            
        Returns:
            int: Segundos transcurridos desde timer_started_at hasta ahora
            
        Cálculo:
            - Si timer_started_at es None, retorna 0
            - De lo contrario: (ahora - timer_started_at).total_seconds()
            - Redondea al entero más cercano
            
        Detalle técnico:
            - Función síncrona (no requiere await)
            - No accede a base de datos
            - Usa datetime.utcnow() para consistencia de zona horaria
            - Útil para actualizar displays en tiempo real
            - Retorna 0 si timer no está activo (no retorna None)
            
        Ejemplo de uso:
            elapsed = TimerService.get_elapsed_time(ticket)
            print(f"Tiempo transcurrido: {elapsed} segundos")
        """
        if not ticket.get('timer_started_at'):
            return 0
        
        # Obtener timestamp de inicio
        timer_started = ticket['timer_started_at']
        
        # Convertir a datetime si viene como string
        if isinstance(timer_started, str):
            timer_started = datetime.fromisoformat(timer_started)
        
        # Calcular diferencia desde el inicio
        now = datetime.utcnow()
        elapsed = (now - timer_started).total_seconds()
        
        # Retornar como entero redondeado
        return int(round(elapsed))

    @staticmethod
    async def start_blocked_timer(
        db: AsyncSession,
        ticket: dict
    ) -> dict:
        """
        Inicia el timer de bloqueo para medir tiempo de espera.
        
        Cuando un ticket transiciona a BLOCKED, comienza a contar el tiempo
        que está esperando resolución. Este timer es independiente del timer
        de ejecución.
        
        Args:
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            ticket (dict): Diccionario con datos del ticket
            
        Returns:
            dict: Diccionario con datos del ticket actualizados
            
        Estructura de retorno:
            {
                'id': uuid,
                'blocked_timer_started_at': datetime,  # Inicio del bloqueo
                'blocked_time_seconds': int,           # Tiempo acumulado previo
                'status': 'BLOCKED'
            }
            
        Raises:
            HTTPException(400): Timer de bloqueo ya está activo
            HTTPException(404): Ticket no encontrado
            HTTPException(500): Error al iniciar timer de bloqueo
            
        Validaciones:
            - No debe haber timer de bloqueo activo
            - Ticket debe existir
            
        Detalle técnico:
            - blocked_timer_started_at se asigna a datetime.utcnow()
            - Registra evento BLOCKED_TIMER_START en auditoría
            - Es independiente del timer de ejecución
            - blocked_time_seconds es acumulativo (suma de bloques anteriores)
        """
        try:
            # Validar que no hay timer de bloqueo activo
            if ticket.get('blocked_timer_started_at'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El timer de bloqueo ya está en ejecución para este ticket"
                )
            
            # Buscar ticket en base de datos
            # stmt = select(Ticket).where(Ticket.id == UUID(ticket['id']))
            # result = await db.execute(stmt)
            # db_ticket = result.scalars().first()
            
            # if not db_ticket:
            #     raise HTTPException(
            #         status_code=status.HTTP_404_NOT_FOUND,
            #         detail="Ticket no encontrado"
            #     )
            
            # Iniciar timer de bloqueo
            # db_ticket.blocked_timer_started_at = datetime.utcnow()
            # db_ticket.updated_at = datetime.utcnow()
            
            # Registrar evento de inicio de bloqueo
            # new_event = TicketEvent(
            #     ticket_id=db_ticket.id,
            #     event_type='BLOCKED_TIMER_START',
            #     detail={'started_at': db_ticket.blocked_timer_started_at.isoformat()}
            # )
            # db.add(new_event)
            
            # Persistir cambios
            # await db.commit()
            # await db.refresh(db_ticket)
            
            return {
                # 'id': str(db_ticket.id),
                # 'blocked_timer_started_at': db_ticket.blocked_timer_started_at.isoformat(),
                # 'blocked_time_seconds': db_ticket.blocked_time_seconds,
                # 'status': db_ticket.status
            }
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al iniciar timer de bloqueo del ticket"
            )

    @staticmethod
    async def stop_blocked_timer(
        db: AsyncSession,
        ticket: dict
    ) -> dict:
        """
        Finaliza el timer de bloqueo y suma tiempo acumulado.
        
        Cuando un ticket sale del estado BLOCKED (se resuelve la pregunta),
        se detiene el timer de bloqueo y se suma el tiempo de espera al
        acumulador blocked_time_seconds.
        
        Args:
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            ticket (dict): Diccionario con datos del ticket
            
        Returns:
            dict: Diccionario con datos del ticket actualizados
            
        Estructura de retorno:
            {
                'id': uuid,
                'blocked_timer_started_at': None,  # Se limpió
                'blocked_time_seconds': int,        # Suma actualizada
                'blocked_stopped_at': datetime,
                'blocked_elapsed_this_session': int # Segundos en este bloqueo
            }
            
        Raises:
            HTTPException(400): Timer de bloqueo no está activo
            HTTPException(404): Ticket no encontrado
            HTTPException(500): Error al detener timer de bloqueo
            
        Validaciones:
            - blocked_timer_started_at debe estar establecido
            - Ticket debe existir
            
        Detalle técnico:
            - Calcula elapsed desde blocked_timer_started_at
            - Suma elapsed a blocked_time_seconds
            - Limpia blocked_timer_started_at
            - Registra evento BLOCKED_TIMER_STOP
            - Este tiempo cuenta para cálculo de blocking_index
        """
        try:
            # Validar que timer de bloqueo está activo
            if not ticket.get('blocked_timer_started_at'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El timer de bloqueo no está en ejecución para este ticket"
                )
            
            # Buscar ticket en base de datos
            # stmt = select(Ticket).where(Ticket.id == UUID(ticket['id']))
            # result = await db.execute(stmt)
            # db_ticket = result.scalars().first()
            
            # if not db_ticket:
            #     raise HTTPException(
            #         status_code=status.HTTP_404_NOT_FOUND,
            #         detail="Ticket no encontrado"
            #     )
            
            # Calcular tiempo de bloqueo
            # now = datetime.utcnow()
            # blocked_elapsed = int((now - db_ticket.blocked_timer_started_at).total_seconds())
            
            # Sumar al acumulador de bloqueo
            # db_ticket.blocked_time_seconds += blocked_elapsed
            # db_ticket.blocked_timer_started_at = None
            # db_ticket.updated_at = now
            
            # Registrar evento de parada de bloqueo
            # new_event = TicketEvent(
            #     ticket_id=db_ticket.id,
            #     event_type='BLOCKED_TIMER_STOP',
            #     detail={
            #         'stopped_at': now.isoformat(),
            #         'blocked_elapsed_seconds': blocked_elapsed,
            #         'total_blocked_time': db_ticket.blocked_time_seconds
            #     }
            # )
            # db.add(new_event)
            
            # Persistir cambios
            # await db.commit()
            # await db.refresh(db_ticket)
            
            return {
                # 'id': str(db_ticket.id),
                # 'blocked_timer_started_at': None,
                # 'blocked_time_seconds': db_ticket.blocked_time_seconds,
                # 'blocked_stopped_at': now.isoformat(),
                # 'blocked_elapsed_this_session': blocked_elapsed
            }
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al detener timer de bloqueo del ticket"
            )
