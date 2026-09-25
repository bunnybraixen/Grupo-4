"""
Modelo de Equipo (Team) para CoreStream.

Un equipo agrupa usuarios (por email) y proyectos, y es la unidad con la que el
workbench decide qué ve cada usuario: un TEAM_LEADER solo ve los proyectos de
su equipo y solo puede asignar tickets a sus miembros.

Antes este dato vivía únicamente en el `localStorage` del navegador del ADMIN
(store `teams` del frontend), así que cualquier sesión nueva —otro navegador,
otro equipo, una ventana privada— arrancaba sin equipos mientras las
aplicaciones y épicas sí llegaban del backend. Persistirlo aquí hace que los
equipos sean los mismos para todos y sobrevivan a la sesión.
"""

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, BaseEntity


class Team(Base, BaseEntity):
    """
    Entidad que representa un equipo de trabajo.

    Atributos:
        name: Nombre del equipo
        description: Descripción opcional
        member_emails: Emails de los miembros (minúsculas) — incluye al líder
        application_ids: IDs (UUID en texto) de las aplicaciones del equipo
    """

    __tablename__ = "teams"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Nombre del equipo que se muestra en la interfaz"
    )

    description: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        doc="Descripción opcional del propósito del equipo"
    )

    # Se guardan como listas JSON en lugar de tablas de asociación: el frontend
    # ya trabaja con ambos datos como arrays simples y así no hay que tocar las
    # tablas de usuarios ni de aplicaciones.
    member_emails: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        doc="Emails (en minúsculas) de los miembros del equipo"
    )

    application_ids: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        doc="IDs de las aplicaciones asignadas a este equipo"
    )
