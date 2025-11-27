from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from enum import Enum
from src.infrastructure.database.base import Base


class OrganizationTypeEnum(str, Enum):
    """Enum para tipo de organização"""
    PERSONAL = "PERSONAL"      # ✅ minúsculas para match com o banco
    ENTERPRISE = "ENTERPRISE"  # ✅ minúsculas para match com o banco


class OrganizationModel(Base):
    """Model SQLAlchemy para Organization"""
    
    __tablename__ = "organizations"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Identifiers
    slug = Column(String(63), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    
    # Type - ✅ CORREÇÃO CRÍTICA: mapeia 'type' (Python) para 'organization_type' (DB)
    type = Column(
        "organization_type",  # ✅ Nome da coluna no banco de dados
        SQLEnum(
            OrganizationTypeEnum,
            name='organization_type',
            create_type=False
        ),
        nullable=False
    )
    
    # Optional Fields
    logo = Column(String(500), nullable=True)
    
    # Access Control
    acl_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # Índices adicionais
    __table_args__ = (
        Index('ix_organizations_slug', 'slug'),
        Index('ix_organizations_organization_type', 'organization_type'),  # ✅ Nome correto
        Index('ix_organizations_acl_id', 'acl_id'),
    )
    
    def __repr__(self):
        return f"<OrganizationModel(id={self.id}, slug={self.slug}, name={self.name}, type={self.type})>"