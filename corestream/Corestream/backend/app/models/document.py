"""
Modelo de Documento para CoreStream.
Define la estructura de los documentos que pueden adjuntarse a épicos o tickets.
Los documentos permiten compartir información adicional como especificaciones, capturas, etc.
"""

from datetime import datetime
from enum import Enum
from uuid import UUID as PyUUID
from sqlalchemy import String, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM

from .base import Base, BaseEntity


class DocumentType(str, Enum):
    """
    Enumeración de tipos de documentos en CoreStream.
    
    Tipos:
        CODE: Fragmentos de código, archivos de configuración
        DOCUMENTATION: Documentación, especificaciones, guías
    """
    CODE = "CODE"
    DOCUMENTATION = "DOCUMENTATION"


class Document(Base, BaseEntity):
    """
    Entidad que representa un Documento en CoreStream.
    
    Los documentos permiten adjuntar archivos a épicos o tickets,
    facilitando la compartición de código, especificaciones, capturas de pantalla, etc.
    
    Atributos principales:
        filename: Nombre original del archivo
        file_path: Ruta de almacenamiento del archivo en el sistema
        file_size: Tamaño del archivo en bytes
        mime_type: Tipo MIME del archivo
        epic_id: Referencia al épico (puede ser NULL)
        ticket_id: Referencia al ticket (puede ser NULL)
        uploaded_by_id: Usuario que subió el documento
        doc_type: Tipo de documento (código o documentación)
    
    Relaciones:
        epic: Épico al que está asociado el documento
        ticket: Ticket al que está asociado el documento
        uploaded_by: Usuario que subió el documento
    
    Índices:
        epic_id: Búsqueda rápida de documentos por épico
        ticket_id: Búsqueda rápida de documentos por ticket
        uploaded_by_id: Búsqueda de documentos por usuario
    
    Notas:
        Un documento debe estar asociado a un épico o un ticket (no ambos).
        La ruta del archivo se gestiona mediante un servicio separado de almacenamiento.
    """
    
    __tablename__ = "documents"
    
    # Nombre original del archivo
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Nombre original del archivo como fue subido por el usuario"
    )
    
    # Ruta del almacenamiento del archivo en el sistema de archivos o nube
    file_path: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        doc="Ruta de almacenamiento del archivo en el sistema de archivos o servicio de nube"
    )
    
    # Tamaño del archivo en bytes
    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Tamaño del archivo en bytes"
    )
    
    # Tipo MIME del archivo
    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Tipo MIME del archivo (ej: application/pdf, image/png)"
    )
    
    # Clave foránea al épico (opcional)
    epic_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("epics.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        doc="Referencia al épico al que está asociado este documento"
    )
    
    # Clave foránea al ticket (opcional)
    ticket_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        doc="Referencia al ticket al que está asociado este documento"
    )
    
    # Clave foránea al usuario que subió el documento
    uploaded_by_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="Referencia al usuario que subió este documento"
    )
    
    # Tipo de documento
    doc_type: Mapped[DocumentType] = mapped_column(
        ENUM(DocumentType, name="document_type_enum"),
        default=DocumentType.DOCUMENTATION,
        nullable=False,
        doc="Tipo de documento: CODE o DOCUMENTATION"
    )
    
    # Relaciones hacia otras entidades
    
    epic = relationship(
        "Epic",
        back_populates="documents",
        foreign_keys=[epic_id],
        doc="Épico al que está asociado este documento"
    )
    
    ticket = relationship(
        "Ticket",
        foreign_keys=[ticket_id],
        doc="Ticket al que está asociado este documento"
    )
    
    uploaded_by = relationship(
        "User",
        back_populates="uploaded_documents",
        foreign_keys=[uploaded_by_id],
        doc="Usuario que subió este documento"
    )
    
    __table_args__ = (
        Index('ix_documents_epic_id', 'epic_id'),
        Index('ix_documents_ticket_id', 'ticket_id'),
        Index('ix_documents_uploaded_by_id', 'uploaded_by_id'),
    )
