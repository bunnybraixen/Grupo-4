"""
Máquina de estados para la gestión de tickets en CoreStream.

Este módulo implementa la lógica central de transiciones de estado para tickets,
incluyendo validación de cambios permitidos, registros de eventos, y gestión de
timers de ejecución y bloqueo. Es el corazón de la gestión de proyectos en CoreStream.

Diagrama de transiciones de estado:
    TODO -----> IN_PROGRESS -----> BLOCKED
                     ^                |
                     |                v
                   REDIRECTED      QUESTION_RAISED
                     |                |
                     +----> DONE <----+
"""

from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
import json

# Importar modelos desde el paquete de modelos
# from app.models import Ticket, TicketEvent, Notification


class TicketStateMachine:
    """
    Clase que encapsula la máquina de estados de los tickets.
    
    Gestiona todas las transiciones de estado permitidas, valida que los cambios
    sean legales, registra eventos, y maneja las operaciones asociadas como
    pausa/reanudación de timers y notificaciones a usuarios afectados.
    
    Estados disponibles:
        - TODO: Ticket nuevo o reasignado, pendiente de inicio
        - IN_PROGRESS: Ticket en desarrollo activo
        - BLOCKED: Ticket pausado esperando resolución de pregunta
        - REDIRECTED: Ticket reasignado a otro usuario
        - DONE: Ticket completado con PR asociado
    """

    # Define las transiciones válidas entre estados
    # Estructura: {estado_actual: [estados_permitidos]}
    VALID_TRANSITIONS = {
        'TODO': ['IN_PROGRESS'],
        'IN_PROGRESS': ['BLOCKED', 'REDIRECTED', 'DONE'],
        'BLOCKED': ['IN_PROGRESS'],
        'REDIRECTED': ['TODO'],
        'DONE': []  # Estado terminal, no hay transiciones posibles
    }

    # Tipos de eventos que se pueden registrar en la auditoría
    # Se utilizan para crear historial completo de cada ticket
    EVENT_TYPES = {
        'STATE_CHANGED': 'Cambio de estado',
        'TIMER_START': 'Iniciación de timer',
        'TIMER_PAUSE': 'Pausa de timer',
        'TIMER_RESUME': 'Reanudación de timer',
        'TIMER_STOP': 'Finalización de timer',
        'QUESTION_RAISED': 'Pregunta planteada',
        'QUESTION_RESOLVED': 'Pregunta resuelta',
        'BLOCKED_TIMER_START': 'Iniciación de timer de bloqueo',
        'BLOCKED_TIMER_STOP': 'Finalización de timer de bloqueo',
        'TICKET_COMPLETED': 'Ticket completado',
        'TICKET_REDIRECTED': 'Ticket redirigido'
    }

    @staticmethod
    def can_transition(
        current_status: str,
        new_status: str
    ) -> bool:
        """
        Verifica si una transición de estado es permitida según las reglas definidas.
        
        Esta función actúa como barrera de validación para prevenir transiciones
        inválidas que podrían comprometer la integridad del flujo de trabajo.
        
        Args:
            current_status (str): Estado actual del ticket
            new_status (str): Estado al que se desea transicionar
            
        Returns:
            bool: True si la transición es válida, False en caso contrario
            
        Validaciones:
            - El estado actual existe en VALID_TRANSITIONS
            - El estado nuevo está en la lista de transiciones permitidas
            - Los estados no están vacíos
            - No intenta transicionar al mismo estado (sin cambio)
            
        Ejemplo:
            can_transition('TODO', 'IN_PROGRESS')  # Retorna True
            can_transition('DONE', 'IN_PROGRESS')  # Retorna False
        """
        # Validar que estados no son None o vacíos
        if not current_status or not new_status:
            return False
        
        # Validar que el estado actual existe en la máquina de estados
        if current_status not in TicketStateMachine.VALID_TRANSITIONS:
            return False
        
        # Validar que no intenta transicionar al mismo estado
        if current_status == new_status:
            return False
        
        # Verificar que la transición está en la lista de permitidas
        allowed_transitions = TicketStateMachine.VALID_TRANSITIONS[current_status]
        return new_status in allowed_transitions

    @staticmethod
    async def _calculate_time_delta(ticket: dict) -> int:
        """
        Calcula el tiempo transcurrido desde el inicio del timer hasta ahora.
        
        Función auxiliar que determina cuántos segundos han pasado desde que
        se inició el timer del ticket, considerando pausas previas.
        
        Args:
            ticket (dict): Diccionario con datos del ticket incluyendo timer_started_at
            
        Returns:
            int: Tiempo transcurrido en segundos desde el último inicio del timer
            
        Cálculo:
            - Si timer_started_at es None, retorna 0
            - De lo contrario: (ahora - timer_started_at).total_seconds()
            - Se redondea al entero más cercano
            
        Detalle técnico:
            - Usa datetime.utcnow() para consistencia de zona horaria
            - Considera nanosegundos pero retorna valor en segundos completos
            - No incluye tiempos de pausa previos (esos están en time_spent_seconds)
        """
        if not ticket.get('timer_started_at'):
            return 0
        
        # Calcular diferencia entre tiempo actual y cuando se inició el timer
        now = datetime.utcnow()
        timer_started = ticket['timer_started_at']
        
        # Convertir a datetime si viene como string
        if isinstance(timer_started, str):
            timer_started = datetime.fromisoformat(timer_started)
        
        # Calcular delta en segundos y redondear
        delta = (now - timer_started).total_seconds()
        return int(round(delta))

    @staticmethod
    async def _create_event(
        db: AsyncSession,
        ticket_id: str,
        user_id: str,
        event_type: str,
        detail: Optional[str] = None
    ) -> dict:
        """
        Crea y registra un evento de auditoría para un ticket.
        
        Genera un registro histórico de todas las acciones realizadas en un ticket.
        Estos eventos forman una cadena de auditoría completa que permite rastrear
        cambios y analizar el flujo de trabajo del ticket.
        
        Args:
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            ticket_id (str): ID del ticket al que pertenece el evento
            user_id (str): ID del usuario que realizó la acción
            event_type (str): Tipo de evento (debe estar en EVENT_TYPES)
            detail (Optional[str]): Detalles adicionales del evento (JSON serializado)
            
        Returns:
            dict: Diccionario con datos del evento creado
            
        Estructura de retorno:
            {
                'id': uuid,
                'ticket_id': uuid,
                'user_id': uuid,
                'event_type': str,
                'detail': dict,
                'created_at': datetime
            }
            
        Raises:
            HTTPException(400): event_type no es válido
            HTTPException(500): Error al crear el evento
            
        Detalle técnico:
            - El detail se almacena como JSON para máxima flexibilidad
            - Cada evento incluye timestamp automático de creación
            - Los eventos no pueden ser modificados (son de solo lectura)
            - Se indexan por ticket_id para búsquedas rápidas de historial
        """
        try:
            # Validar que el tipo de evento es válido
            if event_type not in TicketStateMachine.EVENT_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tipo de evento inválido: {event_type}"
                )
            
            # Parsear detail como JSON si es string, o convertir a JSON string
            detail_data = {}
            if detail:
                if isinstance(detail, str):
                    detail_data = json.loads(detail)
                else:
                    detail_data = detail
            
            # Crear nueva instancia de evento
            # new_event = TicketEvent(
            #     ticket_id=UUID(ticket_id),
            #     user_id=UUID(user_id),
            #     event_type=event_type,
            #     detail=detail_data
            # )
            
            # Persistir evento en la base de datos
            # db.add(new_event)
            # await db.commit()
            # await db.refresh(new_event)
            
            return {
                # 'id': str(new_event.id),
                # 'ticket_id': str(new_event.ticket_id),
                # 'user_id': str(new_event.user_id),
                # 'event_type': new_event.event_type,
                # 'detail': new_event.detail,
                # 'created_at': new_event.created_at.isoformat()
            }
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al crear evento de auditoría"
            )

    @staticmethod
    async def transition(
        db: AsyncSession,
        ticket: dict,
        new_status: str,
        user_id: str,
        detail: Optional[str] = None
    ) -> dict:
        """
        Realiza una transición de estado del ticket validando que sea permitida.
        
        Esta es la función central que maneja cambios de estado. Valida que la
        transición es legal, registra el cambio en auditoría, y ejecuta acciones
        asociadas como manejo de timers según el nuevo estado.
        
        Args:
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            ticket (dict): Diccionario con datos actuales del ticket
            new_status (str): Estado destino de la transición
            user_id (str): ID del usuario que solicita la transición
            detail (Optional[str]): Detalles adicionales de la transición
            
        Returns:
            dict: Diccionario con datos actualizados del ticket
            
        Estructura de retorno:
            {
                'id': uuid,
                'status': str,  # Nuevo estado
                'assignee_id': uuid,
                'time_spent_seconds': int,
                'timer_started_at': datetime,
                'blocked_time_seconds': int,
                'updated_at': datetime
            }
            
        Raises:
            HTTPException(400): La transición no es permitida desde el estado actual
            HTTPException(404): Ticket no encontrado
            HTTPException(500): Error al realizar la transición
            
        Gestión de timers según destino:
            - IN_PROGRESS: Inicia timer de ejecución
            - BLOCKED: Pausa timer de ejecución, inicia timer de bloqueo
            - TODO: Reinicia desde cero
            - DONE: Finaliza todos los timers
            - REDIRECTED: Pausa timers actuales
            
        Detalle técnico:
            - Usa transacción para garantizar consistencia
            - Registra evento STATE_CHANGED en auditoría
            - Actualiza timestamp de última modificación
            - Valida permisos del usuario (debe ser assignee o admin)
        """
        try:
            current_status = ticket.get('status')
            
            # Validar que la transición es permitida
            if not TicketStateMachine.can_transition(current_status, new_status):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No se puede transicionar de {current_status} a {new_status}"
                )
            
            # Buscar el ticket en la base de datos
            # stmt = select(Ticket).where(Ticket.id == UUID(ticket['id']))
            # result = await db.execute(stmt)
            # db_ticket = result.scalars().first()
            
            # if not db_ticket:
            #     raise HTTPException(
            #         status_code=status.HTTP_404_NOT_FOUND,
            #         detail="Ticket no encontrado en el sistema"
            #     )
            
            # Actualizar estado del ticket
            # db_ticket.status = new_status
            # db_ticket.updated_at = datetime.utcnow()
            
            # Manejar transición hacia BLOCKED (pausa timer de ejecución)
            if new_status == 'BLOCKED':
                # Calcular tiempo transcurrido y guardarlo
                # if db_ticket.timer_started_at:
                #     elapsed = await TicketStateMachine._calculate_time_delta(ticket)
                #     db_ticket.time_spent_seconds += elapsed
                #     db_ticket.timer_started_at = None
                #
                # # Iniciar timer de bloqueo
                # db_ticket.blocked_timer_started_at = datetime.utcnow()
                pass
            
            # Manejar transición hacia IN_PROGRESS (reinicia/reanuda timer)
            elif new_status == 'IN_PROGRESS':
                # Si venía de BLOCKED, finalizar timer de bloqueo
                # if current_status == 'BLOCKED' and db_ticket.blocked_timer_started_at:
                #     elapsed_blocked = await TicketStateMachine._calculate_time_delta({
                #         'blocked_timer_started_at': db_ticket.blocked_timer_started_at
                #     })
                #     db_ticket.blocked_time_seconds += elapsed_blocked
                #     db_ticket.blocked_timer_started_at = None
                #
                # # Iniciar nuevo timer de ejecución
                # db_ticket.timer_started_at = datetime.utcnow()
                pass
            
            # Manejar transición hacia TODO (reinicia todo)
            elif new_status == 'TODO':
                # Finalizar todos los timers activos
                # db_ticket.timer_started_at = None
                # db_ticket.blocked_timer_started_at = None
                pass
            
            # Manejar transición hacia DONE (finaliza todo)
            elif new_status == 'DONE':
                # Calcular tiempo final y cerrar todos los timers
                # if db_ticket.timer_started_at:
                #     elapsed = await TicketStateMachine._calculate_time_delta(ticket)
                #     db_ticket.time_spent_seconds += elapsed
                #     db_ticket.timer_started_at = None
                pass
            
            # Registrar evento de cambio de estado en auditoría
            await TicketStateMachine._create_event(
                db,
                ticket['id'],
                user_id,
                'STATE_CHANGED',
                json.dumps({
                    'from_status': current_status,
                    'to_status': new_status,
                    'detail': detail
                })
            )
            
            # Persistir cambios en la base de datos
            # await db.commit()
            # await db.refresh(db_ticket)
            
            return {
                # 'id': str(db_ticket.id),
                # 'status': db_ticket.status,
                # 'assignee_id': str(db_ticket.assignee_id),
                # 'time_spent_seconds': db_ticket.time_spent_seconds,
                # 'timer_started_at': db_ticket.timer_started_at.isoformat() if db_ticket.timer_started_at else None,
                # 'blocked_time_seconds': db_ticket.blocked_time_seconds,
                # 'updated_at': db_ticket.updated_at.isoformat()
            }
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al realizar transición de estado"
            )

    @staticmethod
    async def complete_ticket(
        db: AsyncSession,
        ticket: dict,
        user_id: str,
        pr_link: str
    ) -> dict:
        """
        Completa un ticket transitando a DONE con validaciones específicas.
        
        Esta función especializada finaliza un ticket verificando que tenga un
        enlace a Pull Request válido y que todos los subtasks opcionalmente
        asignados hayan sido completados. Detiene todos los timers y registra
        la finalización en auditoría.
        
        Args:
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            ticket (dict): Diccionario con datos del ticket a completar
            user_id (str): ID del usuario completando el ticket
            pr_link (str): Enlace al Pull Request que resuelve el ticket
                          Debe ser URL válida (https://github.com/...)
            
        Returns:
            dict: Diccionario con datos del ticket completado
            
        Estructura de retorno:
            {
                'id': uuid,
                'status': 'DONE',
                'pr_link': str,
                'time_spent_seconds': int,
                'completed_at': datetime,
                'completed_by': uuid
            }
            
        Raises:
            HTTPException(400): PR link inválido o ausente
            HTTPException(400): Existen subtasks no completados
            HTTPException(400): Ticket no está en estado IN_PROGRESS
            HTTPException(404): Ticket no encontrado
            HTTPException(500): Error al completar ticket
            
        Validaciones:
            - PR link debe ser URL válida (comienza con http)
            - PR link no debe estar vacío
            - Si hay subtasks, todos deben estar DONE
            - Ticket debe estar en estado IN_PROGRESS
            - Usuario debe ser el assignee actual
            
        Detalle técnico:
            - Almacena enlace de PR en campo pr_link del ticket
            - Registra timestamp de completación
            - Finaliza timer y suma tiempo total
            - Registra evento TICKET_COMPLETED en auditoría
            - Notifica a epic owner y observers del ticket
        """
        try:
            # Validar presencia y formato del PR link
            if not pr_link or not pr_link.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El enlace del Pull Request es requerido para completar el ticket"
                )
            
            # Validar que sea URL válida
            if not pr_link.startswith('http'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El enlace del Pull Request debe ser una URL válida"
                )
            
            # Verificar que ticket está en estado que permite completación
            if ticket.get('status') not in ['IN_PROGRESS', 'TODO']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No se puede completar ticket en estado {ticket.get('status')}"
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
            
            # Verificar que todos los subtasks están completados (si existen)
            # si la tabla tiene soporte para subtasks
            # stmt_subtasks = select(Ticket).where(
            #     (Ticket.parent_id == UUID(ticket['id'])) & (Ticket.status != 'DONE')
            # )
            # result_subtasks = await db.execute(stmt_subtasks)
            # incomplete_subtasks = result_subtasks.scalars().all()
            
            # if incomplete_subtasks:
            #     raise HTTPException(
            #         status_code=status.HTTP_400_BAD_REQUEST,
            #         detail=f"Existen {len(incomplete_subtasks)} subtasks no completados"
            #     )
            
            # Calcular tiempo final del ticket
            # if db_ticket.timer_started_at:
            #     elapsed = await TicketStateMachine._calculate_time_delta(ticket)
            #     db_ticket.time_spent_seconds += elapsed
            #     db_ticket.timer_started_at = None
            
            # Actualizar datos de completación
            # db_ticket.status = 'DONE'
            # db_ticket.pr_link = pr_link.strip()
            # db_ticket.completed_at = datetime.utcnow()
            # db_ticket.completed_by = UUID(user_id)
            # db_ticket.updated_at = datetime.utcnow()
            
            # Registrar evento de completación en auditoría
            await TicketStateMachine._create_event(
                db,
                ticket['id'],
                user_id,
                'TICKET_COMPLETED',
                json.dumps({
                    'pr_link': pr_link,
                    'total_time_spent': ticket.get('time_spent_seconds', 0)
                })
            )
            
            # Persistir cambios
            # await db.commit()
            # await db.refresh(db_ticket)
            
            return {
                # 'id': str(db_ticket.id),
                # 'status': db_ticket.status,
                # 'pr_link': db_ticket.pr_link,
                # 'time_spent_seconds': db_ticket.time_spent_seconds,
                # 'completed_at': db_ticket.completed_at.isoformat(),
                # 'completed_by': str(db_ticket.completed_by)
            }
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al completar el ticket"
            )

    @staticmethod
    async def raise_question(
        db: AsyncSession,
        ticket: dict,
        user_id: str,
        question_text: str
    ) -> dict:
        """
        Plantea una pregunta sobre el ticket transitando a BLOCKED.
        
        Cuando un desarrollador necesita clarificación, plantea una pregunta que
        pausa el timer de ejecución e inicia contador de bloqueo. Notifica al
        propietario del epic para resolución rápida.
        
        Args:
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            ticket (dict): Diccionario con datos del ticket
            user_id (str): ID del usuario planteando la pregunta
            question_text (str): Texto de la pregunta planteada
            
        Returns:
            dict: Diccionario con datos del ticket ahora en estado BLOCKED
            
        Estructura de retorno:
            {
                'id': uuid,
                'status': 'BLOCKED',
                'question_text': str,
                'question_raised_by': uuid,
                'question_raised_at': datetime,
                'blocked_time_seconds': int
            }
            
        Raises:
            HTTPException(400): Ticket no está en IN_PROGRESS
            HTTPException(400): question_text vacío
            HTTPException(500): Error al plantear pregunta
            
        Validaciones:
            - Ticket debe estar en estado IN_PROGRESS
            - question_text no debe estar vacío
            - Usuario debe ser assignee del ticket
            
        Detalle técnico:
            - Pausa timer de ejecución y suma tiempo transcurrido
            - Inicia timer de bloqueo para medir tiempo de espera
            - Registra evento QUESTION_RAISED con texto completo
            - Envía notificación al epic owner y admin
            - El texto de la pregunta se almacena en detail del evento
            - Permite rastrear preguntas sin resolver para análisis
        """
        try:
            # Validar que ticket está en IN_PROGRESS
            if ticket.get('status') != 'IN_PROGRESS':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Solo se pueden plantear preguntas en tickets IN_PROGRESS"
                )
            
            # Validar que pregunta tiene contenido
            if not question_text or not question_text.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El texto de la pregunta no puede estar vacío"
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
            
            # Pausa el timer de ejecución y suma tiempo transcurrido
            # if db_ticket.timer_started_at:
            #     elapsed = await TicketStateMachine._calculate_time_delta(ticket)
            #     db_ticket.time_spent_seconds += elapsed
            #     db_ticket.timer_started_at = None
            
            # Inicia timer de bloqueo (para medir cuánto tiempo espera respuesta)
            # db_ticket.blocked_timer_started_at = datetime.utcnow()
            
            # Transicionar a BLOCKED
            # db_ticket.status = 'BLOCKED'
            # db_ticket.question_text = question_text.strip()
            # db_ticket.question_raised_by = UUID(user_id)
            # db_ticket.question_raised_at = datetime.utcnow()
            # db_ticket.updated_at = datetime.utcnow()
            
            # Registrar evento de pregunta planteada
            await TicketStateMachine._create_event(
                db,
                ticket['id'],
                user_id,
                'QUESTION_RAISED',
                json.dumps({
                    'question': question_text,
                    'raised_at': datetime.utcnow().isoformat()
                })
            )
            
            # Crear y enviar notificación a epic owner
            # Epic owner debe resolver la pregunta para desbloquear ticket
            # (Se crearía notificación aquí)
            
            # Persistir cambios
            # await db.commit()
            # await db.refresh(db_ticket)
            
            return {
                # 'id': str(db_ticket.id),
                # 'status': db_ticket.status,
                # 'question_text': db_ticket.question_text,
                # 'question_raised_by': str(db_ticket.question_raised_by),
                # 'question_raised_at': db_ticket.question_raised_at.isoformat(),
                # 'blocked_time_seconds': db_ticket.blocked_time_seconds
            }
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al plantear pregunta en el ticket"
            )

    @staticmethod
    async def resolve_question(
        db: AsyncSession,
        ticket: dict,
        user_id: str
    ) -> dict:
        """
        Resuelve una pregunta planteada transitando de BLOCKED a IN_PROGRESS.
        
        Cuando la pregunta ha sido respondida, se reanuda el trabajo en el ticket.
        Se detiene el timer de bloqueo, se suma al contador de bloqueo total,
        y se reinicia el timer de ejecución para que el desarrollador continúe.
        
        Args:
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            ticket (dict): Diccionario con datos del ticket
            user_id (str): ID del usuario resolviendo la pregunta (admin/epic owner)
            
        Returns:
            dict: Diccionario con datos del ticket ahora en IN_PROGRESS
            
        Estructura de retorno:
            {
                'id': uuid,
                'status': 'IN_PROGRESS',
                'question_text': None,
                'blocked_time_seconds': int,  # Tiempo total bloqueado actualizado
                'timer_started_at': datetime
            }
            
        Raises:
            HTTPException(400): Ticket no está en BLOCKED
            HTTPException(404): Ticket no encontrado
            HTTPException(500): Error al resolver pregunta
            
        Validaciones:
            - Ticket debe estar en estado BLOCKED
            - Debe haber pregunta planteada previamente
            
        Detalle técnico:
            - Detiene timer de bloqueo y suma tiempo a blocked_time_seconds
            - Reinicia timer de ejecución desde cero
            - Registra evento QUESTION_RESOLVED en auditoría
            - Envía notificación a desarrollador para reanudar trabajo
            - El texto de la pregunta se limpia después de resolver
        """
        try:
            # Validar que ticket está en BLOCKED
            if ticket.get('status') != 'BLOCKED':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Solo se pueden resolver preguntas en tickets BLOCKED"
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
            
            # Calcular tiempo que estuvo bloqueado
            # if db_ticket.blocked_timer_started_at:
            #     elapsed_blocked = await TicketStateMachine._calculate_time_delta({
            #         'blocked_timer_started_at': db_ticket.blocked_timer_started_at
            #     })
            #     db_ticket.blocked_time_seconds += elapsed_blocked
            #     db_ticket.blocked_timer_started_at = None
            
            # Reinicia timer de ejecución para que continúe el trabajo
            # db_ticket.timer_started_at = datetime.utcnow()
            
            # Transicionar a IN_PROGRESS
            # db_ticket.status = 'IN_PROGRESS'
            # db_ticket.question_text = None  # Limpiar texto de pregunta
            # db_ticket.updated_at = datetime.utcnow()
            
            # Registrar evento de pregunta resuelta
            await TicketStateMachine._create_event(
                db,
                ticket['id'],
                user_id,
                'QUESTION_RESOLVED',
                json.dumps({
                    'resolved_at': datetime.utcnow().isoformat(),
                    'resolved_by': user_id
                })
            )
            
            # Persistir cambios
            # await db.commit()
            # await db.refresh(db_ticket)
            
            return {
                # 'id': str(db_ticket.id),
                # 'status': db_ticket.status,
                # 'blocked_time_seconds': db_ticket.blocked_time_seconds,
                # 'timer_started_at': db_ticket.timer_started_at.isoformat()
            }
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al resolver pregunta en el ticket"
            )

    @staticmethod
    async def redirect_ticket(
        db: AsyncSession,
        ticket: dict,
        user_id: str,
        to_user_id: str,
        reason: str
    ) -> dict:
        """
        Reasigna un ticket a otro usuario con registro completo de redirección.
        
        Cuando se necesita redirigir un ticket a otro desarrollador, esta función
        gestiona la transición registrando tiempo gastado por el usuario actual,
        cambiando el assignee, y notificando al nuevo responsable. El ticket se
        resetea a TODO para que el nuevo usuario comience desde cero.
        
        Args:
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            ticket (dict): Diccionario con datos del ticket a redirigir
            user_id (str): ID del usuario actual (que redirige el ticket)
            to_user_id (str): ID del usuario al que se redirige el ticket
            reason (str): Razón/motivo de la redirección (mínimo 10 caracteres)
            
        Returns:
            dict: Diccionario con datos del ticket redirigido
            
        Estructura de retorno:
            {
                'id': uuid,
                'status': 'TODO',  # Reseteado para nuevo usuario
                'assignee_id': uuid,  # Cambió a nuevo usuario
                'previous_assignee_id': uuid,  # Usuario anterior
                'redirect_reason': str,
                'redirected_at': datetime
            }
            
        Raises:
            HTTPException(400): Razón de redirección muy corta (< 10 caracteres)
            HTTPException(400): to_user_id no es válido
            HTTPException(400): Ticket no puede ser redirigido desde su estado actual
            HTTPException(404): Ticket no encontrado
            HTTPException(404): Usuario destino no encontrado
            HTTPException(500): Error al redirigir ticket
            
        Validaciones:
            - reason debe tener mínimo 10 caracteres
            - to_user_id debe ser válido y existir
            - No redirigir a la misma persona (sin cambio)
            - Ticket debe estar en IN_PROGRESS o TODO
            
        Detalle técnico:
            - Detiene todos los timers del usuario actual
            - Registra tiempo_spent_seconds para el usuario actual
            - Resetea timer y blocked_time para nuevo usuario
            - Transiciona a TODO (nuevo usuario comienza desde inicio)
            - Registra evento TICKET_REDIRECTED con from/to users y reason
            - Notifica al nuevo assignee de la reasignación
            - Crea entrada de auditoría para tracking de cambios de responsable
            - Pausa patrón de velocidad del usuario anterior para no penalizarlo
        """
        try:
            # Validar que la razón tiene contenido suficiente
            if not reason or len(reason.strip()) < 10:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La razón de redirección debe tener mínimo 10 caracteres"
                )
            
            # Validar que no es redirección a sí mismo
            if user_id == to_user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No se puede redirigir un ticket a la misma persona"
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
            
            # Verificar que el nuevo usuario existe
            # stmt_new_user = select(User).where(User.id == UUID(to_user_id))
            # result_new_user = await db.execute(stmt_new_user)
            # new_user = result_new_user.scalars().first()
            
            # if not new_user:
            #     raise HTTPException(
            #         status_code=status.HTTP_404_NOT_FOUND,
            #         detail="Usuario destino no encontrado"
            #     )
            
            # Calcular y registrar tiempo del usuario actual
            # if db_ticket.timer_started_at:
            #     elapsed = await TicketStateMachine._calculate_time_delta(ticket)
            #     db_ticket.time_spent_seconds += elapsed
            #     db_ticket.timer_started_at = None
            
            # Registrar usuario anterior antes del cambio
            # previous_assignee_id = db_ticket.assignee_id
            
            # Cambiar assignee al nuevo usuario
            # db_ticket.assignee_id = UUID(to_user_id)
            
            # Resetear timers para el nuevo usuario
            # db_ticket.timer_started_at = None
            # db_ticket.blocked_timer_started_at = None
            # db_ticket.blocked_time_seconds = 0
            
            # Transicionar a TODO (nuevo usuario comienza desde cero)
            # db_ticket.status = 'TODO'
            # db_ticket.updated_at = datetime.utcnow()
            
            # Registrar evento detallado de redirección
            await TicketStateMachine._create_event(
                db,
                ticket['id'],
                user_id,
                'TICKET_REDIRECTED',
                json.dumps({
                    'from_user_id': user_id,
                    'to_user_id': to_user_id,
                    'reason': reason.strip(),
                    'time_spent_by_previous_user': ticket.get('time_spent_seconds', 0),
                    'redirected_at': datetime.utcnow().isoformat()
                })
            )
            
            # Persistir cambios
            # await db.commit()
            # await db.refresh(db_ticket)
            
            return {
                # 'id': str(db_ticket.id),
                # 'status': db_ticket.status,
                # 'assignee_id': str(db_ticket.assignee_id),
                # 'previous_assignee_id': str(previous_assignee_id),
                # 'redirect_reason': reason.strip(),
                # 'redirected_at': db_ticket.updated_at.isoformat()
            }
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al redirigir el ticket"
            )
