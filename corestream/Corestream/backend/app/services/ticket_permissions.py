"""
Helpers de autorización sobre tickets, compartidos por routers/tickets.py y
routers/subtasks.py (plan fase 4).

Antes de esta fase, tickets.py y epics.py no usaban require_role NI UNA SOLA
VEZ. Lo único que había era _require_non_admin, que hace lo contrario:
bloquea al ADMIN de las acciones de "trabajo" (start/complete/question) pero
no restringe nada más. Verificado en la auditoría: cualquier DEVELOPER podía
borrar cualquier ticket (204), o iniciar un ticket ajeno (200, y el ticket se
reasignaba a quien llamaba — ver claim_or_assert_assignee más abajo).

Matriz de permisos completa en docs/RBAC.md.
"""

from __future__ import annotations

from fastapi import HTTPException, status

from app.models import Ticket, User

_MANAGER_ROLES = {"ADMIN", "TEAM_LEADER"}


def get_role_name(user: User) -> str:
    """Extrae el nombre del rol de forma segura, sin lazy-load implícito."""
    role_obj = getattr(user, "role", None)
    if role_obj is None:
        return ""
    return role_obj.name if hasattr(role_obj, "name") else str(role_obj)


def is_admin_or_leader(user: User) -> bool:
    return get_role_name(user) in _MANAGER_ROLES


def require_non_admin(current_user: User) -> None:
    """
    Bloquea a los ADMIN de las acciones de "trabajo" sobre un ticket
    (start/complete/question): admins gestionan el sistema, no ejecutan el
    trabajo. Ya existía como función local en tickets.py; se centraliza aquí
    para que subtasks.py pueda aplicar la misma regla sin duplicarla.
    """
    if get_role_name(current_user) == "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Los administradores no pueden ejecutar acciones de trabajo en tickets",
        )


def require_admin_or_leader(current_user: User) -> None:
    """
    Para acciones de gestión que NO son "trabajo" del ticket: crear, borrar,
    resolver una pregunta bloqueante ajena. A diferencia de
    require_non_admin, aquí el ADMIN SÍ está permitido — es quien construye
    la estructura (aplicaciones, épicas, tickets) y quien puede intervenir
    para desbloquear a un desarrollador.
    """
    if not is_admin_or_leader(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol ADMIN o TEAM_LEADER",
        )


def assert_can_manage_ticket(ticket: Ticket, current_user: User) -> None:
    """
    Para acciones de gestión sobre UN ticket concreto (editar campos, mover
    de épica, reordenar en el tablero): ADMIN/TEAM_LEADER siempre puede;
    un DEVELOPER solo si el ticket está asignado a él.
    """
    if is_admin_or_leader(current_user):
        return
    if ticket.assignee_id == current_user.id:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permiso para modificar este ticket",
    )


def assert_is_current_assignee(ticket: Ticket, current_user: User) -> None:
    """
    Para completar o levantar una pregunta: solo quien tiene el ticket
    asignado EN ESTE MOMENTO — sin excepción de rol. Un TEAM_LEADER que no
    es el asignado no puede completar el trabajo de otro; para eso existe
    /redirect, no esto. (El ADMIN ya queda fuera antes, vía require_non_admin.)
    """
    if ticket.assignee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el usuario asignado puede realizar esta acción",
        )


def claim_or_assert_assignee(ticket: Ticket, current_user: User) -> None:
    """
    Para /start: si el ticket no tiene asignado, current_user lo reclama
    (pasa a estar asignado a sí mismo — flujo de "tirar de la cola"). Si ya
    tiene un asignado distinto, se rechaza.

    Antes, TicketStateMachine.transition_to_in_progress asignaba el ticket a
    quien llamara SIEMPRE, sin comprobar nada — así que cualquier DEVELOPER
    podía "robarse" un ticket ya asignado a otro con solo llamar a /start.
    Esta función corta ese camino ANTES de llegar a la máquina de estados:
    para cuando esta se ejecuta, ticket.assignee_id ya es el correcto, y su
    propia asignación (redundante en ese punto) es un no-op.
    """
    if ticket.assignee_id is None:
        ticket.assignee_id = current_user.id
    elif ticket.assignee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Este ticket ya está asignado a otro usuario",
        )
