from __future__ import annotations

from datetime import datetime
from uuid import UUID as PyUUID
from uuid import uuid4

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Base declarativa para SQLAlchemy 2.0.

    CONVENCIÓN: toda relationship() del proyecto debe declarar
    lazy="raise_on_sql", no el "raise" a secas ni el "select" por defecto.

    Motivo: esta aplicación usa exclusivamente AsyncSession, que no soporta
    lazy loading implícito — cualquier relación no precargada con
    selectinload()/joinedload() revienta con MissingGreenlet en cuanto algo
    intenta leerla, típicamente al serializar la respuesta con Pydantic. Antes
    de esto, ese fallo solo se veía en producción, ante la primera petición
    real que tocara esa ruta de código; se detectaron así tres 500 en
    endpoints ya en uso (ver tests/integration, xfail de la fase 2.3).

    lazy="raise_on_sql" adelanta ese fallo a un error explícito
    (InvalidRequestError: 'Modelo.relación' is not available due to
    lazy='raise_on_sql') apenas se toca la relación sin haberla precargado —
    útil en desarrollo y letal en CI si se olvida un selectinload.

    Se descartó lazy="raise" (sin el sufijo _on_sql): revienta incluso cuando
    la relación se puede resolver sin ninguna consulta — por ejemplo, un
    many-to-one cuya columna de FK ya está cargada y es NULL. Varias
    @property de los modelos (linked_ticket_title, epic_title...) hacen
    "if self.relacion else None", y con lazy="raise" esa comprobación
    reventaba siempre, incluso para tickets sin relación alguna. raise_on_sql
    resuelve ese caso trivial sin tocar la base y solo revienta cuando de
    verdad haría falta una consulta.
    """


class BaseEntity:
    """Mixin con campos comunes para entidades persistentes."""

    __abstract__ = True

    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
