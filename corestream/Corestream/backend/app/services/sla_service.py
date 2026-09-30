"""
Servicio de SLA (Service Level Agreement) a NIVEL DE TICKET para CoreStream.

El SLA NO se define por Sprint: se define por TICKET, a partir de su
prioridad/severidad y de los objetivos configurados por el ADMIN
(`sla_configs`). Para cada ticket se calcula:

    - Tiempo transcurrido y restante del SLA de respuesta (desde `created_at`
      hasta `first_response_at`).
    - Tiempo transcurrido y restante del SLA de resolución (desde `created_at`
      hasta `completed_at`/`updated_at`, o hasta ahora si sigue abierto).
    - Incumplimientos (BREACHED) y alertas de "próximo a vencer" (AT_RISK).

Todos los cálculos son deterministas y sin IO, de modo que el mismo código se
usa para un ticket individual, para el listado del Workbench y para las
métricas agregadas de un Sprint.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from math import ceil
from typing import Any, Iterable, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import SLAConfig, Ticket, TicketPriority

# ---------------------------------------------------------------------------
# Objetivos por defecto (minutos) cuando no existe configuración para una
# prioridad. Tupla: (respuesta, resolución).
# ---------------------------------------------------------------------------
DEFAULT_TARGETS: dict[str, tuple[int, int]] = {
    TicketPriority.LOW.value: (480, 4320),
    TicketPriority.MEDIUM.value: (240, 1440),
    TicketPriority.HIGH.value: (120, 480),
    TicketPriority.URGENT.value: (60, 240),
}

DEFAULT_WARN_THRESHOLD_PERCENT = 80

# Estados posibles de cada objetivo del SLA
STATE_ON_TRACK = "ON_TRACK"
STATE_AT_RISK = "AT_RISK"
STATE_BREACHED = "BREACHED"
STATE_MET = "MET"
STATE_NOT_APPLICABLE = "NOT_APPLICABLE"

# Estados terminales del ticket para el cálculo del SLA de resolución
DONE_STATUSES = {"DONE", "COMPLETED"}


# ---------------------------------------------------------------------------
# Utilidades internas
# ---------------------------------------------------------------------------

def _priority_value(ticket: Ticket) -> str:
    """Normaliza la prioridad del ticket a su valor string (LOW/MEDIUM/HIGH/URGENT)."""
    priority = getattr(ticket, "priority", None)
    return str(getattr(priority, "value", priority) or TicketPriority.MEDIUM.value).upper()


def _status_value(ticket: Ticket) -> str:
    """Normaliza el estado del ticket a su valor string (TODO/IN_PROGRESS/...)."""
    status = getattr(ticket, "status", None)
    return str(getattr(status, "value", status) or "").upper()


def _as_aware(value: Optional[datetime]) -> Optional[datetime]:
    """
    Normaliza un datetime a timezone-aware (UTC).

    La BD mezcla timestamps con y sin zona (`func.now()` vs `datetime.now`), así
    que sin esto la resta de fechas puede lanzar TypeError.
    """
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _minutes(delta: timedelta) -> int:
    """Convierte una diferencia de tiempo en minutos (redondeo hacia arriba)."""
    return int(ceil(delta.total_seconds() / 60))


def _evaluate(
    opened_at: datetime,
    deadline: datetime,
    now: datetime,
    warn_at: datetime,
    closed_at: Optional[datetime] = None,
) -> tuple[str, int, int]:
    """
    Evalúa un objetivo de SLA.

    Returns:
        (estado, minutos_transcurridos, minutos_restantes). Los minutos
        restantes son negativos cuando el objetivo ya venció.
    """
    if closed_at is not None:
        elapsed = _minutes(closed_at - opened_at)
        return (
            STATE_BREACHED if closed_at > deadline else STATE_MET,
            elapsed,
            _minutes(deadline - closed_at),
        )

    if now > deadline:
        return STATE_BREACHED, _minutes(now - opened_at), -_minutes(now - deadline)
    if now >= warn_at:
        return STATE_AT_RISK, _minutes(now - opened_at), _minutes(deadline - now)
    return STATE_ON_TRACK, _minutes(now - opened_at), _minutes(deadline - now)


def _overall(*states: str) -> str:
    """Combina los estados de respuesta y resolución en un estado global."""
    if STATE_BREACHED in states:
        return STATE_BREACHED
    if STATE_AT_RISK in states:
        return STATE_AT_RISK
    if all(state == STATE_MET for state in states):
        return STATE_MET
    if STATE_NOT_APPLICABLE in states:
        return STATE_NOT_APPLICABLE
    return STATE_ON_TRACK


# ---------------------------------------------------------------------------
# Configuración (persistida por el ADMIN)
# ---------------------------------------------------------------------------

async def load_sla_configs(db: AsyncSession) -> dict[str, dict[str, int]]:
    """
    Carga las reglas de SLA activas indexadas por prioridad.

    Si una prioridad no tiene fila propia, se usa el objetivo por defecto
    (`DEFAULT_TARGETS`) para que el SLA nunca quede sin calcular.
    """
    configs: dict[str, dict[str, int]] = {}

    for priority, (response, resolution) in DEFAULT_TARGETS.items():
        configs[priority] = {
            "response_minutes": response,
            "resolution_minutes": resolution,
            "warn_threshold_percent": DEFAULT_WARN_THRESHOLD_PERCENT,
        }

    result = await db.execute(select(SLAConfig))
    for config in result.scalars().all():
        if not config.is_active:
            continue
        configs[str(getattr(config.priority, "value", config.priority)).upper()] = {
            "response_minutes": max(1, int(config.response_minutes)),
            "resolution_minutes": max(1, int(config.resolution_minutes)),
            "warn_threshold_percent": max(
                1, min(100, int(config.warn_threshold_percent or DEFAULT_WARN_THRESHOLD_PERCENT))
            ),
        }

    return configs


async def ensure_default_configs(db: AsyncSession) -> list[SLAConfig]:
    """
    Garantiza que exista una fila de configuración por cada prioridad.

    Así el panel de ADMIN en `/admin/builder` siempre tiene algo que editar en
    lugar de una tabla vacía.
    """
    result = await db.execute(select(SLAConfig))
    existing = {
        str(getattr(config.priority, "value", config.priority)).upper(): config
        for config in result.scalars().all()
    }

    created: list[SLAConfig] = []
    for priority in TicketPriority:
        if priority.value in existing:
            continue
        response, resolution = DEFAULT_TARGETS[priority.value]
        config = SLAConfig(
            priority=priority,
            response_minutes=response,
            resolution_minutes=resolution,
            warn_threshold_percent=DEFAULT_WARN_THRESHOLD_PERCENT,
            is_active=True,
        )
        db.add(config)
        created.append(config)

    if created:
        await db.commit()
        for config in created:
            await db.refresh(config)

    return created


# ---------------------------------------------------------------------------
# Cálculo por ticket
# ---------------------------------------------------------------------------

def compute_ticket_sla(
    ticket: Ticket,
    configs: Optional[dict[str, dict[str, int]]] = None,
    now: Optional[datetime] = None,
) -> dict[str, Any]:
    """
    Calcula el estado de SLA de un ticket.

    Args:
        ticket: Ticket ORM (debe tener `created_at`, `priority`, `status`).
        configs: Reglas por prioridad; si es None se usan los valores por defecto.
        now: Momento de referencia (inyectable para pruebas).

    Returns:
        Diccionario serializable con tiempos objetivo, transcurridos, restantes,
        estados por objetivo, estado global y banderas de incumplimiento.
    """
    configs = configs or {}
    now = _as_aware(now) or datetime.now(timezone.utc)

    priority = _priority_value(ticket)
    default_response, default_resolution = DEFAULT_TARGETS.get(
        priority, DEFAULT_TARGETS[TicketPriority.MEDIUM.value]
    )
    rule = configs.get(priority, {})
    response_minutes = int(rule.get("response_minutes", default_response))
    resolution_minutes = int(rule.get("resolution_minutes", default_resolution))
    warn_percent = int(rule.get("warn_threshold_percent", DEFAULT_WARN_THRESHOLD_PERCENT))

    created_at = _as_aware(getattr(ticket, "created_at", None)) or now
    response_due_at = created_at + timedelta(minutes=response_minutes)
    resolution_due_at = created_at + timedelta(minutes=resolution_minutes)
    response_warn_at = response_due_at - timedelta(
        minutes=max(1, int(response_minutes * (100 - warn_percent) / 100))
    )
    resolution_warn_at = resolution_due_at - timedelta(
        minutes=max(1, int(resolution_minutes * (100 - warn_percent) / 100))
    )

    first_response_at = _as_aware(getattr(ticket, "first_response_at", None))
    completed_at = _as_aware(
        getattr(ticket, "completed_at", None) or getattr(ticket, "updated_at", None)
    )

    response_state, response_elapsed, response_remaining = _evaluate(
        created_at, response_due_at, now, response_warn_at, first_response_at
    )

    is_done = _status_value(ticket) in DONE_STATUSES
    if is_done and completed_at is not None:
        resolution_state, resolution_elapsed, resolution_remaining = _evaluate(
            created_at, resolution_due_at, now, resolution_warn_at, completed_at
        )
    else:
        resolution_state, resolution_elapsed, resolution_remaining = _evaluate(
            created_at, resolution_due_at, now, resolution_warn_at
        )

    state = _overall(response_state, resolution_state)

    # Próximo vencimiento relevante para las alertas
    pending_deadlines: list[tuple[datetime, str]] = []
    if response_state in (STATE_ON_TRACK, STATE_AT_RISK):
        pending_deadlines.append((response_due_at, "RESPONSE"))
    if not is_done and resolution_state in (STATE_ON_TRACK, STATE_AT_RISK):
        pending_deadlines.append((resolution_due_at, "RESOLUTION"))

    next_deadline: Optional[datetime] = None
    next_metric: Optional[str] = None
    if pending_deadlines:
        next_deadline, next_metric = min(pending_deadlines, key=lambda item: item[0])

    return {
        "ticket_id": str(getattr(ticket, "id", "")),
        "title": getattr(ticket, "title", None),
        "ticket_status": _status_value(ticket),
        # `epic_title` / `sprint_name` son propiedades del modelo que devuelven
        # None si la relación no viene precargada (evitan lazy-load async).
        "epic_title": getattr(ticket, "epic_title", None),
        "sprint_name": getattr(ticket, "sprint_name", None),
        "sprint_id": str(ticket.sprint_id) if getattr(ticket, "sprint_id", None) else None,
        "assignee_id": str(ticket.assignee_id) if getattr(ticket, "assignee_id", None) else None,
        "due_date": getattr(ticket, "due_date", None).isoformat()
        if getattr(ticket, "due_date", None)
        else None,
        "priority": priority,
        "response_target_minutes": response_minutes,
        "resolution_target_minutes": resolution_minutes,
        "warn_threshold_percent": warn_percent,
        "created_at": created_at.isoformat(),
        "first_response_at": first_response_at.isoformat() if first_response_at else None,
        "response_due_at": response_due_at.isoformat(),
        "resolution_due_at": resolution_due_at.isoformat(),
        "response_elapsed_minutes": response_elapsed,
        "resolution_elapsed_minutes": resolution_elapsed,
        "response_remaining_minutes": response_remaining,
        "resolution_remaining_minutes": resolution_remaining,
        "response_state": response_state,
        "resolution_state": resolution_state,
        "state": state,
        "is_breached": state == STATE_BREACHED,
        "is_at_risk": state == STATE_AT_RISK,
        "is_compliant": state in (STATE_MET, STATE_ON_TRACK),
        "is_resolved": is_done,
        "next_deadline_at": next_deadline.isoformat() if next_deadline else None,
        "next_deadline_metric": next_metric,
        "minutes_to_next_deadline": _minutes(next_deadline - now) if next_deadline else None,
    }


def build_sla_map(
    tickets: Iterable[Ticket],
    configs: Optional[dict[str, dict[str, int]]] = None,
    now: Optional[datetime] = None,
) -> dict[str, dict[str, Any]]:
    """Calcula el SLA de una colección de tickets indexado por `ticket_id`."""
    return {str(ticket.id): compute_ticket_sla(ticket, configs, now) for ticket in tickets}


def summarize_sla(statuses: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """
    Agrega una lista de estados de SLA en métricas para un Sprint o proyecto.

    Returns:
        Conteos por estado, tasa de cumplimiento y tasa de incumplimiento.
    """
    items = list(statuses)
    total = len(items)
    breached = sum(1 for item in items if item.get("state") == STATE_BREACHED)
    at_risk = sum(1 for item in items if item.get("state") == STATE_AT_RISK)
    met = sum(1 for item in items if item.get("state") == STATE_MET)
    on_track = sum(1 for item in items if item.get("state") == STATE_ON_TRACK)

    compliant = met + on_track
    return {
        "total": total,
        "on_track": on_track,
        "at_risk": at_risk,
        "breached": breached,
        "met": met,
        "compliance_rate": round((compliant / total) * 100, 2) if total else 0.0,
        "breach_rate": round((breached / total) * 100, 2) if total else 0.0,
    }
