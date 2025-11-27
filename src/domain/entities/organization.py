from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
import re
from enum import Enum

from src.domain.entities._base import BaseId, AggregateRoot, ValueObject

# =============================================================================
# VALUE OBJECTS
# =============================================================================

class OrganizationId(BaseId):
    """Identificador único para organizações"""
    pass

class ACLId(BaseId):
    """Identificador único para ACL"""
    pass

class Slug(ValueObject):
    """Slug URL-friendly e único para a organização"""
    
    def __init__(self, slug: str):
        self._slug = slug
        self._validate()
    
    def _validate(self) -> None:
        if not self._slug or not isinstance(self._slug, str):
            raise ValueError("Slug deve ser uma string válida")
        
        cleaned_slug = self._slug.strip().lower()
        
        if not cleaned_slug:
            raise ValueError("Slug não pode estar vazio")
        
        if len(cleaned_slug) < 3:
            raise ValueError("Slug deve ter pelo menos 3 caracteres")
        
        if len(cleaned_slug) > 63:
            raise ValueError("Slug não pode exceder 63 caracteres")
        
        if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', cleaned_slug):
            raise ValueError("Slug deve conter apenas letras minúsculas, números e hífens, sem iniciar ou terminar com hífen")
        
        if cleaned_slug.startswith('-') or cleaned_slug.endswith('-'):
            raise ValueError("Slug não pode iniciar ou terminar com hífen")
        
        if '--' in cleaned_slug:
            raise ValueError("Slug não pode conter hífens consecutivos")
    
    @property
    def value(self) -> str:
        return self._slug.strip().lower()
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Slug):
            return False
        return self.value == other.value

class OrganizationType(str, Enum):
    """Tipo da organização"""
    PERSONAL = 'PERSONAL'
    ENTERPRISE = 'ENTERPRISE'

class OrganizationName(ValueObject):
    """Nome da organização"""
    
    def __init__(self, name: str):
        self._name = name
        self._validate()
    
    def _validate(self) -> None:
        if not self._name or not isinstance(self._name, str):
            raise ValueError("Nome da organização deve ser uma string válida")
        
        cleaned_name = self._name.strip()
        
        if not cleaned_name:
            raise ValueError("Nome da organização não pode estar vazio")
        
        if len(cleaned_name) < 2:
            raise ValueError("Nome da organização deve ter pelo menos 2 caracteres")
        
        if len(cleaned_name) > 100:
            raise ValueError("Nome da organização não pode exceder 100 caracteres")
    
    @property
    def value(self) -> str:
        return self._name.strip()
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, OrganizationName):
            return False
        return self.value == other.value

class Logo(ValueObject):
    """Logo da organização (URL ou caminho)"""
    
    def __init__(self, logo: str):
        self._logo = logo
        self._validate()
    
    def _validate(self) -> None:
        if not self._logo or not isinstance(self._logo, str):
            raise ValueError("Logo deve ser uma string válida")
        
        cleaned_logo = self._logo.strip()
        
        if not cleaned_logo:
            raise ValueError("Logo não pode estar vazio")
        
        if len(cleaned_logo) > 500:
            raise ValueError("Logo não pode exceder 500 caracteres")
    
    @property
    def value(self) -> str:
        return self._logo.strip()
    
    @property
    def is_url(self) -> bool:
        """Verifica se é uma URL"""
        return self.value.startswith(('http://', 'https://'))
    
    @property
    def is_path(self) -> bool:
        """Verifica se é um caminho local"""
        return not self.is_url
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Logo):
            return False
        return self.value == other.value

# =============================================================================
# ENTITY
# =============================================================================

class Organization(AggregateRoot):
    """
    Agregado raiz representando uma organização no sistema.
    
    Uma organização pode ser do tipo PERSONAL (individual) ou ENTERPRISE (empresarial),
    possui identificação única através de slug imutável, e pode ter controle de acesso
    através de ACL dedicada.
    """
    
    def __init__(
        self,
        id: OrganizationId,
        slug: Slug,
        name: OrganizationName,
        organization_type: OrganizationType,
        logo: Optional[Logo] = None,
        acl_id: Optional[ACLId] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        super().__init__()
        
        self._id = id
        self._slug = slug
        self._name = name
        self._type = organization_type
        self._logo = logo
        self._acl_id = acl_id
        self._created_at = created_at or datetime.now()
        self._updated_at = updated_at or datetime.now()
        
        self._validate()
    
    def _validate(self) -> None:
        self._validate_required_fields()
        self._validate_types()
        self._validate_business_rules()
    
    def _validate_required_fields(self) -> None:
        if not self._id:
            self.notification.add_error("ID da organização é obrigatório")
        
        if not self._slug:
            self.notification.add_error("Slug é obrigatório")
        
        if not self._name:
            self.notification.add_error("Nome da organização é obrigatório")
        
        if not self._type:
            self.notification.add_error("Tipo da organização é obrigatório")
    
    def _validate_types(self) -> None:
        if self._id and not isinstance(self._id, OrganizationId):
            self.notification.add_error("ID da organização deve ser do tipo OrganizationId")
        
        if self._slug and not isinstance(self._slug, Slug):
            self.notification.add_error("Slug deve ser do tipo Slug")
        
        if self._name and not isinstance(self._name, OrganizationName):
            self.notification.add_error("Nome da organização deve ser do tipo OrganizationName")
        
        if not isinstance(self._type, OrganizationType):
            self.notification.add_error("Tipo da organização deve ser do tipo OrganizationType")
        
        if self._logo and not isinstance(self._logo, Logo):
            self.notification.add_error("Logo deve ser do tipo Logo")
        
        if self._acl_id and not isinstance(self._acl_id, ACLId):
            self.notification.add_error("ID do ACL deve ser do tipo ACLId")
        
        if not isinstance(self._created_at, datetime):
            self.notification.add_error("Data de criação deve ser do tipo datetime")
        
        if not isinstance(self._updated_at, datetime):
            self.notification.add_error("Data de atualização deve ser do tipo datetime")
    
    def _validate_business_rules(self) -> None:
        if self._updated_at < self._created_at:
            self.notification.add_error("Data de atualização não pode ser anterior à data de criação")
        
        if self._created_at > datetime.now():
            self.notification.add_error("Data de criação não pode ser futura")
    
    @property
    def id(self) -> OrganizationId:
        return self._id
    
    @property
    def slug(self) -> Slug:
        return self._slug
    
    @property
    def name(self) -> OrganizationName:
        return self._name
    
    @property
    def organization_type(self) -> OrganizationType:
        return self._type
    
    @property
    def logo(self) -> Optional[Logo]:
        return self._logo
    
    @property
    def acl_id(self) -> Optional[ACLId]:
        return self._acl_id
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    def update_name(self, name: OrganizationName) -> None:
        if not name:
            self.notification.add_error("Nome da organização é obrigatório")
            return
        
        if not isinstance(name, OrganizationName):
            self.notification.add_error("Nome da organização deve ser do tipo OrganizationName")
            return
        
        if self._name.value == name.value:
            self.notification.add_error("Nome já está definido com este valor")
            return
        
        self._name = name
        self._updated_at = datetime.now()
    
    def update_logo(self, logo: Logo) -> None:
        if not logo:
            self.notification.add_error("Logo é obrigatório")
            return
        
        if not isinstance(logo, Logo):
            self.notification.add_error("Logo deve ser do tipo Logo")
            return
        
        self._logo = logo
        self._updated_at = datetime.now()
    
    def remove_logo(self) -> None:
        if not self._logo:
            self.notification.add_error("Organização não possui logo para remover")
            return
        
        self._logo = None
        self._updated_at = datetime.now()
    
    def assign_acl(self, acl_id: ACLId) -> None:
        if not acl_id:
            self.notification.add_error("ID do ACL é obrigatório")
            return
        
        if not isinstance(acl_id, ACLId):
            self.notification.add_error("ID do ACL deve ser do tipo ACLId")
            return
        
        if self._acl_id:
            self.notification.add_error("Organização já possui ACL associada")
            return
        
        self._acl_id = acl_id
        self._updated_at = datetime.now()
    
    def remove_acl(self) -> None:
        if not self._acl_id:
            self.notification.add_error("Organização não possui ACL para remover")
            return
        
        self._acl_id = None
        self._updated_at = datetime.now()
    
    def is_personal(self) -> bool:
        return self._type == OrganizationType.PERSONAL
    
    def is_enterprise(self) -> bool:
        return self._type == OrganizationType.ENTERPRISE
    
    def has_logo(self) -> bool:
        return self._logo is not None
    
    def has_acl(self) -> bool:
        return self._acl_id is not None
    
    def get_display_info(self) -> Dict[str, str]:
        """Retorna informações de exibição da organização"""
        return {
            'name': self._name.value,
            'slug': self._slug.value,
            'type': self._type.value,
            'logo': self._logo.value if self._logo else None,
            'has_acl': str(self.has_acl())
        }
    
    def get_metadata(self) -> Dict[str, Any]:
        """Retorna metadados da organização"""
        return {
            'created_at': self._created_at,
            'updated_at': self._updated_at,
            'is_personal': self.is_personal(),
            'is_enterprise': self.is_enterprise(),
            'has_logo': self.has_logo(),
            'has_acl': self.has_acl(),
            'slug': self._slug.value
        }