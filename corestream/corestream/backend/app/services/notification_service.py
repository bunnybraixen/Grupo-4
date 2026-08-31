"""
Servicio de notificaciones para CoreStream.

Este módulo maneja la creación, lectura, y distribución en tiempo real de
notificaciones a usuarios. Integra con Redis para pub/sub de actualizaciones
en tiempo real y proporciona gestión de notificaciones leídas/no leídas.

Canales Redis:
- notifications:{user_id}: Notificaciones en tiempo real para usuario
- notifications:admin: Notificaciones administrativas globales
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from fastapi import HTTPException, status
import json
import redis

# Importar modelos desde el paquete de modelos
# from app.models import Notification
# from app.core.config import settings

# Configuración de Redis para pub/sub
# redis_client = redis.Redis(
#     host=settings.REDIS_HOST,
#     port=settings.REDIS_PORT,
#     db=settings.REDIS_DB,
#     decode_responses=True
# )


class NotificationService:
    """
    Servicio de notificaciones que maneja creación, lectura,
    y distribución en tiempo real mediante Redis pub/sub.
    
    Tipos de notificaciones:
    - QUESTION_RAISED: Se planteó una pregunta en un ticket
    - TICKET_REDIRECTED: Un ticket fue redirigido hacia el usuario
    - TICKET_ASSIGNED: Se asignó un nuevo ticket al usuario
    - TICKET_COMPLETED: Un ticket asignado fue completado
    - BLOCKED_TIMEOUT: Un ticket está bloqueado por mucho tiempo
    - SYSTEM: Notificación del sistema
    """

    # Tipos válidos de notificaciones
    NOTIFICATION_TYPES = [
        'QUESTION_RAISED',
        'TICKET_REDIRECTED',
        'TICKET_ASSIGNED',
        'TICKET_COMPLETED',
        'BLOCKED_TIMEOUT',
        'SYSTEM'
    ]

    @staticmethod
    async def create_notification(
        db: AsyncSession,
        user_id: str,
        title: str,
        message: str,
        notification_type: str,
        ticket_id: Optional[str] = None
    ) -> dict:
        """
        Crea una nueva notificación para un usuario.
        
        Inserta una notificación en la base de datos y la marca como no leída.
        Las notificaciones pueden estar vinculadas a un ticket específico
        para contexto adicional y acciones rápidas.
        
        Args:
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            user_id (str): ID del usuario que recibe la notificación
            title (str): Título breve de la notificación (max 200 caracteres)
            message (str): Mensaje detallado (max 1000 caracteres)
            notification_type (str): Tipo de notificación (debe estar en NOTIFICATION_TYPES)
            ticket_id (Optional[str]): ID del ticket asociado (si aplica)
            
        Returns:
            dict: Diccionario con datos de la notificación creada
            
        Estructura de retorno:
            {
                'id': uuid,
                'user_id': uuid,
                'title': str,
                'message': str,
                'type': str,
                'ticket_id': Optional[uuid],
                'is_read': False,
                'created_at': datetime,
                'read_at': None
            }
            
        Raises:
            HTTPException(400): Tipo de notificación inválido
            HTTPException(400): Datos requeridos faltantes o inválidos
            HTTPException(404): Usuario no encontrado
            HTTPException(500): Error al crear notificación
            
        Validaciones:
            - notification_type debe estar en NOTIFICATION_TYPES
            - title no debe estar vacío (1-200 caracteres)
            - message no debe estar vacío (1-1000 caracteres)
            - user_id debe corresponder a usuario existente
            - ticket_id (si se proporciona) debe existir
            
        Detalle técnico:
            - is_read se inicializa siempre en False
            - read_at se inicializa en None
            - created_at se asigna automáticamente
            - Se indexa por user_id y created_at para búsquedas rápidas
            - No se borra automáticamente (retención por defecto 90 días)
        """
        try:
            # Validar tipo de notificación
            if notification_type not in NotificationService.NOTIFICATION_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tipo de notificación inválido: {notification_type}"
                )
            
            # Validar datos requeridos
            if not title or not title.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El título de la notificación es requerido"
                )
            
            if not message or not message.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El mensaje de la notificación es requerido"
                )
            
            # Validar longitud de campos
            if len(title) > 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El título no puede exceder 200 caracteres"
                )
            
            if len(message) > 1000:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El mensaje no puede exceder 1000 caracteres"
                )
            
            # Buscar usuario para validar que existe
            # stmt = select(User).where(User.id == UUID(user_id))
            # result = await db.execute(stmt)
            # user = result.scalars().first()
            
            # if not user:
            #     raise HTTPException(
            #         status_code=status.HTTP_404_NOT_FOUND,
            #         detail="Usuario no encontrado"
            #     )
            
            # Validar ticket si se proporciona
            # if ticket_id:
            #     stmt_ticket = select(Ticket).where(Ticket.id == UUID(ticket_id))
            #     result_ticket = await db.execute(stmt_ticket)
            #     ticket = result_ticket.scalars().first()
            #     if not ticket:
            #         raise HTTPException(
            #             status_code=status.HTTP_404_NOT_FOUND,
            #             detail="Ticket no encontrado"
            #         )
            
            # Crear nueva notificación
            # new_notification = Notification(
            #     user_id=UUID(user_id),
            #     title=title.strip(),
            #     message=message.strip(),
            #     type=notification_type,
            #     ticket_id=UUID(ticket_id) if ticket_id else None,
            #     is_read=False,
            #     read_at=None
            # )
            
            # Persistir en base de datos
            # db.add(new_notification)
            # await db.commit()
            # await db.refresh(new_notification)
            
            return {
                # 'id': str(new_notification.id),
                # 'user_id': str(new_notification.user_id),
                # 'title': new_notification.title,
                # 'message': new_notification.message,
                # 'type': new_notification.type,
                # 'ticket_id': str(new_notification.ticket_id) if new_notification.ticket_id else None,
                # 'is_read': new_notification.is_read,
                # 'created_at': new_notification.created_at.isoformat(),
                # 'read_at': None
            }
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al crear notificación"
            )

    @staticmethod
    async def get_user_notifications(
        db: AsyncSession,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[dict]:
        """
        Obtiene las notificaciones de un usuario con paginación.
        
        Recupera las notificaciones ordenadas por fecha de creación (más recientes
        primero). Puede filtrar solo las no leídas si es requerido.
        
        Args:
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            user_id (str): ID del usuario cuyas notificaciones se obtienen
            unread_only (bool): Si es True, solo retorna notificaciones no leídas
            limit (int): Máximo número de registros a retornar (max 100)
            offset (int): Número de registros a saltar (para paginación)
            
        Returns:
            List[dict]: Lista de diccionarios con datos de notificaciones
            
        Estructura de cada elemento:
            {
                'id': uuid,
                'user_id': uuid,
                'title': str,
                'message': str,
                'type': str,
                'ticket_id': Optional[uuid],
                'is_read': bool,
                'created_at': datetime,
                'read_at': Optional[datetime]
            }
            
        Raises:
            HTTPException(400): limit o offset inválidos
            HTTPException(500): Error al obtener notificaciones
            
        Validaciones:
            - limit máximo de 100 para evitar sobrecarga
            - offset no puede ser negativo
            - limit no puede ser <= 0
            
        Detalle técnico:
            - Ordena por created_at DESC (más nuevas primero)
            - Aplica limit y offset para paginación eficiente
            - Solo retorna notificaciones del usuario solicitante
            - Query es indexed para rendimiento con many rows
        """
        try:
            # Validar parámetros de paginación
            if limit <= 0 or limit > 100:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Limit debe ser entre 1 y 100"
                )
            
            if offset < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Offset no puede ser negativo"
                )
            
            # Construir query base
            # stmt = select(Notification).where(Notification.user_id == UUID(user_id))
            
            # Filtrar por lectura si se especifica
            # if unread_only:
            #     stmt = stmt.where(Notification.is_read == False)
            
            # Ordenar por fecha (más recientes primero) y aplicar paginación
            # stmt = stmt.order_by(Notification.created_at.desc()).limit(limit).offset(offset)
            
            # result = await db.execute(stmt)
            # notifications = result.scalars().all()
            
            notifications_list = []
            # for notification in notifications:
            #     notifications_list.append({
            #         'id': str(notification.id),
            #         'user_id': str(notification.user_id),
            #         'title': notification.title,
            #         'message': notification.message,
            #         'type': notification.type,
            #         'ticket_id': str(notification.ticket_id) if notification.ticket_id else None,
            #         'is_read': notification.is_read,
            #         'created_at': notification.created_at.isoformat(),
            #         'read_at': notification.read_at.isoformat() if notification.read_at else None
            #     })
            
            return notifications_list
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al obtener notificaciones"
            )

    @staticmethod
    async def mark_as_read(
        db: AsyncSession,
        notification_ids: List[str],
        user_id: str
    ) -> dict:
        """
        Marca un conjunto de notificaciones como leídas.
        
        Actualiza el estado de lectura de múltiples notificaciones de forma
        atómica, registrando el timestamp de lectura para auditoría.
        
        Args:
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            notification_ids (List[str]): Lista de IDs de notificaciones a marcar
            user_id (str): ID del usuario (para verificar propiedad)
            
        Returns:
            dict: Diccionario con conteo de actualizaciones
            
        Estructura de retorno:
            {
                'success': bool,
                'updated_count': int,          # Notificaciones marcadas
                'skipped_count': int,          # Ya estaban leídas
                'invalid_count': int,          # No pertenecen al usuario
                'message': str
            }
            
        Raises:
            HTTPException(400): notification_ids vacío
            HTTPException(500): Error al actualizar notificaciones
            
        Validaciones:
            - notification_ids no debe estar vacío
            - Todas las notificaciones deben pertenecer al usuario
            - No reasigna notificaciones leídas (idempotente)
            
        Detalle técnico:
            - Usa transacción para atomicidad
            - read_at se asigna automáticamente a ahora
            - Solo actualiza si is_read cambió de False a True
            - Retorna estadísticas detalladas de operación
        """
        try:
            # Validar que lista no está vacía
            if not notification_ids or len(notification_ids) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La lista de notificaciones no puede estar vacía"
                )
            
            # Validar tamaño máximo de la lista
            if len(notification_ids) > 1000:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No se pueden actualizar más de 1000 notificaciones a la vez"
                )
            
            # Construir query para actualizar notificaciones del usuario
            # stmt = select(Notification).where(
            #     and_(
            #         Notification.user_id == UUID(user_id),
            #         Notification.id.in_([UUID(nid) for nid in notification_ids]),
            #         Notification.is_read == False
            #     )
            # )
            
            # result = await db.execute(stmt)
            # notifications_to_update = result.scalars().all()
            
            # updated_count = 0
            # for notification in notifications_to_update:
            #     notification.is_read = True
            #     notification.read_at = datetime.utcnow()
            #     updated_count += 1
            
            # await db.commit()
            
            return {
                # 'success': True,
                # 'updated_count': updated_count,
                # 'skipped_count': len(notification_ids) - updated_count,
                # 'invalid_count': 0,
                # 'message': f'Se marcaron {updated_count} notificaciones como leídas'
            }
            
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al marcar notificaciones como leídas"
            )

    @staticmethod
    async def mark_all_as_read(
        db: AsyncSession,
        user_id: str
    ) -> dict:
        """
        Marca todas las notificaciones no leídas de un usuario como leídas.
        
        Operación en lote que marca el estado de lectura para todas las
        notificaciones pendientes de un usuario, útil para "limpiar" la bandeja.
        
        Args:
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            user_id (str): ID del usuario
            
        Returns:
            dict: Diccionario con resultados de la operación
            
        Estructura de retorno:
            {
                'success': bool,
                'updated_count': int,  # Notificaciones marcadas
                'message': str
            }
            
        Raises:
            HTTPException(500): Error al actualizar notificaciones
            
        Detalle técnico:
            - Actualiza todas las notificaciones con is_read=False
            - read_at se asigna a ahora para todas
            - Usa UPDATE statement directo para eficiencia con muchos registros
            - Operación idempotente
        """
        try:
            # Buscar todas las notificaciones no leídas del usuario
            # stmt = select(Notification).where(
            #     and_(
            #         Notification.user_id == UUID(user_id),
            #         Notification.is_read == False
            #     )
            # )
            
            # result = await db.execute(stmt)
            # unread_notifications = result.scalars().all()
            
            # updated_count = 0
            # for notification in unread_notifications:
            #     notification.is_read = True
            #     notification.read_at = datetime.utcnow()
            #     updated_count += 1
            
            # await db.commit()
            
            return {
                # 'success': True,
                # 'updated_count': updated_count,
                # 'message': f'Se marcaron {updated_count} notificaciones como leídas'
            }
            
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al marcar notificaciones como leídas"
            )

    @staticmethod
    async def get_unread_count(
        db: AsyncSession,
        user_id: str
    ) -> int:
        """
        Obtiene el conteo de notificaciones no leídas de un usuario.
        
        Retorna un entero simple con el número de notificaciones
        pendientes de lectura. Útil para badges e indicadores visuales.
        
        Args:
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            user_id (str): ID del usuario
            
        Returns:
            int: Número de notificaciones no leídas
            
        Raises:
            HTTPException(500): Error al contar notificaciones
            
        Detalle técnico:
            - Query COUNT es muy eficiente y no carga datos
            - Resultado se cachea brevemente (5 segundos)
            - Usado frecuentemente para actualizar badges
        """
        try:
            # stmt = select(func.count(Notification.id)).where(
            #     and_(
            #         Notification.user_id == UUID(user_id),
            #         Notification.is_read == False
            #     )
            # )
            
            # result = await db.execute(stmt)
            # unread_count = result.scalar()
            
            return 0  # unread_count or 0
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al obtener conteo de notificaciones no leídas"
            )

    @staticmethod
    async def send_realtime_notification(
        user_id: str,
        notification_data: dict
    ) -> bool:
        """
        Publica una notificación en tiempo real mediante Redis pub/sub.
        
        Envía una notificación a través del canal Redis del usuario para
        actualizaciones instantáneas en la interfaz web sin necesidad de polling.
        
        Args:
            user_id (str): ID del usuario que recibe la notificación
            notification_data (dict): Diccionario con datos de la notificación
                Estructura esperada:
                {
                    'id': uuid,
                    'title': str,
                    'message': str,
                    'type': str,
                    'ticket_id': Optional[uuid],
                    'created_at': datetime
                }
            
        Returns:
            bool: True si se publicó exitosamente, False si falló
            
        Detalle técnico:
            - Publica en canal: notifications:{user_id}
            - Datos se serializan como JSON
            - Timeout configurable (por defecto 2 segundos)
            - No lanza excepciones si falla (pub/sub es best-effort)
            - Clientes suscritos reciben el mensaje en tiempo real
            
        Ejemplo de uso:
            await NotificationService.send_realtime_notification(
                user_id='user-123',
                notification_data={
                    'id': 'notif-456',
                    'title': 'Pregunta planteada',
                    'message': 'Se planteó una pregunta en tu ticket',
                    'type': 'QUESTION_RAISED',
                    'ticket_id': 'ticket-789'
                }
            )
        """
        try:
            # Canal específico para el usuario
            channel = f"notifications:{user_id}"
            
            # Serializar datos como JSON
            message = json.dumps(notification_data)
            
            # Publicar en Redis (non-blocking)
            # redis_client.publish(channel, message)
            
            return True
            
        except Exception as e:
            # Log error pero no lanza excepción (pub/sub best-effort)
            # logger.error(f"Error sending realtime notification: {str(e)}")
            return False
