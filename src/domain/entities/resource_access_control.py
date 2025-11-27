from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from src.domain.entities._base import BaseId, AggregateRoot, ValueObject

# =============================================================================
# VALUE OBJECTS
# =============================================================================

class ResourceAccessControlId(BaseId):
    """Identificador único para controle de acesso a recursos"""
    pass

class ResourceId(BaseId):
    """Identificador único de um recurso"""
    pass

class OrganizationId(BaseId):
    """Identificador único de uma organização"""
    pass

class OwnerId(BaseId):
    """Identificador único do proprietário do recurso"""
    pass

class PrincipalId(BaseId):
    """Identificador único de um principal (organização, equipe ou usuário)"""
    pass

class ResourceType(str, Enum):
    """Tipo de recurso que pode ter controle de acesso"""
    AGENTS = 'AGENTS'
    ORGANIZATION = 'ORGANIZATION'
    TEAMSPACE = 'TEAMSPACE'
    KNOWLEDGE_BASE = 'KNOWLEDGE_BASE'
    TOOLS = 'TOOLS'
    MODELS = 'MODELS'

class PrincipalType(str, Enum):
    """Tipo de principal que pode receber permissões"""
    ORGANIZATION = 'ORGANIZATION'
    TEAM = 'TEAM'
    USER = 'USER'

class ResourceRole(str, Enum):
    """Papéis disponíveis para acesso a recursos"""
    FULL_ACCESS = 'FULL_ACCESS'
    EDITOR = 'EDITOR'
    USER = 'USER'
    VIEWER = 'VIEWER'

class Principal(ValueObject):
    """Representa um principal (entidade que pode receber permissões)"""
    
    def __init__(self, principal_type: PrincipalType, principal_id: PrincipalId):
        self._principal_type = principal_type
        self._principal_id = principal_id
        self._validate()
    
    def _validate(self) -> None:
        if not self._principal_type:
            raise ValueError("Tipo do principal é obrigatório")
        
        if not isinstance(self._principal_type, PrincipalType):
            raise ValueError("Tipo do principal deve ser do tipo PrincipalType")
        
        if not self._principal_id:
            raise ValueError("ID do principal é obrigatório")
        
        if not isinstance(self._principal_id, PrincipalId):
            raise ValueError("ID do principal deve ser do tipo PrincipalId")
    
    @property
    def principal_type(self) -> PrincipalType:
        return self._principal_type
    
    @property
    def principal_id(self) -> PrincipalId:
        return self._principal_id
    
    def is_organization(self) -> bool:
        return self._principal_type == PrincipalType.ORGANIZATION
    
    def is_team(self) -> bool:
        return self._principal_type == PrincipalType.TEAM
    
    def is_user(self) -> bool:
        return self._principal_type == PrincipalType.USER
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Principal):
            return False
        return (
            self._principal_type == other._principal_type and
            self._principal_id.value == other._principal_id.value
        )
    
    def __hash__(self) -> int:
        return hash((self._principal_type.value, self._principal_id.value))
    
    def to_dict(self) -> Dict[str, str]:
        return {
            'type': self._principal_type.value,
            'principal_id': str(self._principal_id.value)
        }

class AllowEntry(ValueObject):
    """Entrada de permissão associando um principal a papéis"""
    
    def __init__(self, principal: Principal, roles: List[ResourceRole]):
        self._principal = principal
        self._roles = roles
        self._validate()
    
    def _validate(self) -> None:
        if not self._principal:
            raise ValueError("Principal é obrigatório")
        
        if not isinstance(self._principal, Principal):
            raise ValueError("Principal deve ser do tipo Principal")
        
        if not self._roles:
            raise ValueError("Lista de papéis não pode estar vazia")
        
        if not isinstance(self._roles, list):
            raise ValueError("Papéis devem ser uma lista")
        
        if not all(isinstance(role, ResourceRole) for role in self._roles):
            raise ValueError("Todos os papéis devem ser do tipo ResourceRole")
        
        if len(self._roles) != len(set(self._roles)):
            raise ValueError("Não pode haver papéis duplicados")
        
        self._validate_role_hierarchy()
    
    def _validate_role_hierarchy(self) -> None:
        if ResourceRole.FULL_ACCESS in self._roles and len(self._roles) > 1:
            raise ValueError("FULL_ACCESS não pode ser combinado com outros papéis")
        
        if ResourceRole.EDITOR in self._roles and ResourceRole.VIEWER in self._roles:
            raise ValueError("EDITOR já inclui permissões de VIEWER")
        
        if ResourceRole.USER in self._roles and ResourceRole.VIEWER in self._roles:
            raise ValueError("USER já inclui permissões de VIEWER")
    
    @property
    def principal(self) -> Principal:
        return self._principal
    
    @property
    def roles(self) -> List[ResourceRole]:
        return self._roles.copy()
    
    def has_role(self, role: ResourceRole) -> bool:
        return role in self._roles
    
    def has_full_access(self) -> bool:
        return ResourceRole.FULL_ACCESS in self._roles
    
    def can_edit(self) -> bool:
        return (
            ResourceRole.FULL_ACCESS in self._roles or
            ResourceRole.EDITOR in self._roles
        )
    
    def can_use(self) -> bool:
        return (
            ResourceRole.FULL_ACCESS in self._roles or
            ResourceRole.EDITOR in self._roles or
            ResourceRole.USER in self._roles
        )
    
    def can_view(self) -> bool:
        return len(self._roles) > 0
    
    def can_delete(self) -> bool:
        return (
            ResourceRole.FULL_ACCESS in self._roles or
            ResourceRole.EDITOR in self._roles
        )
    
    def can_share(self) -> bool:
        return ResourceRole.FULL_ACCESS in self._roles
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, AllowEntry):
            return False
        return (
            self._principal == other._principal and
            set(self._roles) == set(other._roles)
        )
    
    def __hash__(self) -> int:
        return hash((self._principal, tuple(sorted(r.value for r in self._roles))))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'principal': self._principal.to_dict(),
            'roles': [role.value for role in self._roles]
        }

# =============================================================================
# ENTITY
# =============================================================================

class ResourceAccessControl(AggregateRoot):
    """
    Agregado raiz representando o controle de acesso a recursos.
    
    Gerencia permissões de acesso a diferentes tipos de recursos
    (agentes, organizações, espaços de equipe, bases de conhecimento, ferramentas, modelos)
    através de entradas de permissão que associam principals (organizações, equipes, usuários)
    a papéis específicos (FULL_ACCESS, EDITOR, USER, VIEWER).
    """
    
    def __init__(
        self,
        id: ResourceAccessControlId,
        resource_type: ResourceType,
        resource_id: ResourceId,
        organization_id: OrganizationId,
        owner_id: OwnerId,
        allow_entries: Optional[List[AllowEntry]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        super().__init__()
        
        self._id = id
        self._resource_type = resource_type
        self._resource_id = resource_id
        self._organization_id = organization_id
        self._owner_id = owner_id
        self._allow_entries = allow_entries or []
        self._created_at = created_at or datetime.now()
        self._updated_at = updated_at or datetime.now()
        
        self._validate()
    
    def _validate(self) -> None:
        self._validate_required_fields()
        self._validate_types()
        self._validate_business_rules()
    
    def _validate_required_fields(self) -> None:
        if not self._id:
            self.notification.add_error("ID do controle de acesso é obrigatório")
        
        if not self._resource_type:
            self.notification.add_error("Tipo do recurso é obrigatório")
        
        if not self._resource_id:
            self.notification.add_error("ID do recurso é obrigatório")
        
        if not self._organization_id:
            self.notification.add_error("ID da organização é obrigatório")
        
        if not self._owner_id:
            self.notification.add_error("ID do proprietário é obrigatório")
    
    def _validate_types(self) -> None:
        if self._id and not isinstance(self._id, ResourceAccessControlId):
            self.notification.add_error("ID do controle de acesso deve ser do tipo ResourceAccessControlId")
        
        if self._resource_type and not isinstance(self._resource_type, ResourceType):
            self.notification.add_error("Tipo do recurso deve ser do tipo ResourceType")
        
        if self._resource_id and not isinstance(self._resource_id, ResourceId):
            self.notification.add_error("ID do recurso deve ser do tipo ResourceId")
        
        if self._organization_id and not isinstance(self._organization_id, OrganizationId):
            self.notification.add_error("ID da organização deve ser do tipo OrganizationId")
        
        if self._owner_id and not isinstance(self._owner_id, OwnerId):
            self.notification.add_error("ID do proprietário deve ser do tipo OwnerId")
        
        if not isinstance(self._allow_entries, list):
            self.notification.add_error("Entradas de permissão devem ser uma lista")
        
        if self._allow_entries and not all(isinstance(entry, AllowEntry) for entry in self._allow_entries):
            self.notification.add_error("Todas as entradas de permissão devem ser do tipo AllowEntry")
        
        if not isinstance(self._created_at, datetime):
            self.notification.add_error("Data de criação deve ser do tipo datetime")
        
        if not isinstance(self._updated_at, datetime):
            self.notification.add_error("Data de atualização deve ser do tipo datetime")
    
    def _validate_business_rules(self) -> None:
        if self._updated_at < self._created_at:
            self.notification.add_error("Data de atualização não pode ser anterior à data de criação")
        
        if self._created_at > datetime.now():
            self.notification.add_error("Data de criação não pode ser futura")
        
        principal_set = set()
        for entry in self._allow_entries:
            if entry.principal in principal_set:
                self.notification.add_error(f"Principal duplicado encontrado: {entry.principal.principal_id.value}")
            principal_set.add(entry.principal)
    
    @property
    def id(self) -> ResourceAccessControlId:
        return self._id
    
    @property
    def resource_type(self) -> ResourceType:
        return self._resource_type
    
    @property
    def resource_id(self) -> ResourceId:
        return self._resource_id
    
    @property
    def organization_id(self) -> OrganizationId:
        return self._organization_id
    
    @property
    def owner_id(self) -> OwnerId:
        return self._owner_id
    
    @property
    def allow_entries(self) -> List[AllowEntry]:
        return self._allow_entries.copy()
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    def add_allow_entry(self, allow_entry: AllowEntry) -> None:
        if not allow_entry:
            self.notification.add_error("Entrada de permissão é obrigatória")
            return
        
        if not isinstance(allow_entry, AllowEntry):
            self.notification.add_error("Entrada de permissão deve ser do tipo AllowEntry")
            return
        
        if self._find_entry_by_principal(allow_entry.principal):
            self.notification.add_error("Principal já possui permissões definidas")
            return
        
        self._allow_entries.append(allow_entry)
        self._updated_at = datetime.now()
    
    def remove_allow_entry(self, principal: Principal) -> None:
        if not principal:
            self.notification.add_error("Principal é obrigatório")
            return
        
        if not isinstance(principal, Principal):
            self.notification.add_error("Principal deve ser do tipo Principal")
            return
        
        entry = self._find_entry_by_principal(principal)
        
        if not entry:
            self.notification.add_error("Principal não possui permissões definidas")
            return
        
        self._allow_entries.remove(entry)
        self._updated_at = datetime.now()
    
    def update_allow_entry(self, principal: Principal, new_roles: List[ResourceRole]) -> None:
        if not principal:
            self.notification.add_error("Principal é obrigatório")
            return
        
        if not isinstance(principal, Principal):
            self.notification.add_error("Principal deve ser do tipo Principal")
            return
        
        if not new_roles:
            self.notification.add_error("Lista de papéis não pode estar vazia")
            return
        
        entry = self._find_entry_by_principal(principal)
        
        if not entry:
            self.notification.add_error("Principal não possui permissões definidas")
            return
        
        try:
            new_entry = AllowEntry(principal, new_roles)
            self._allow_entries.remove(entry)
            self._allow_entries.append(new_entry)
            self._updated_at = datetime.now()
        except ValueError as e:
            self.notification.add_error(str(e))
    
    def grant_full_access(self, principal: Principal) -> None:
        self._grant_role(principal, [ResourceRole.FULL_ACCESS])
    
    def grant_editor_access(self, principal: Principal) -> None:
        self._grant_role(principal, [ResourceRole.EDITOR])
    
    def grant_user_access(self, principal: Principal) -> None:
        self._grant_role(principal, [ResourceRole.USER])
    
    def grant_viewer_access(self, principal: Principal) -> None:
        self._grant_role(principal, [ResourceRole.VIEWER])
    
    def _grant_role(self, principal: Principal, roles: List[ResourceRole]) -> None:
        if not principal:
            self.notification.add_error("Principal é obrigatório")
            return
        
        existing_entry = self._find_entry_by_principal(principal)
        
        if existing_entry:
            self.update_allow_entry(principal, roles)
        else:
            try:
                new_entry = AllowEntry(principal, roles)
                self.add_allow_entry(new_entry)
            except ValueError as e:
                self.notification.add_error(str(e))
    
    def revoke_access(self, principal: Principal) -> None:
        self.remove_allow_entry(principal)
    
    def has_access(self, principal: Principal) -> bool:
        return self._find_entry_by_principal(principal) is not None
    
    def can_view(self, principal: Principal) -> bool:
        entry = self._find_entry_by_principal(principal)
        return entry.can_view() if entry else False
    
    def can_use(self, principal: Principal) -> bool:
        entry = self._find_entry_by_principal(principal)
        return entry.can_use() if entry else False
    
    def can_edit(self, principal: Principal) -> bool:
        entry = self._find_entry_by_principal(principal)
        return entry.can_edit() if entry else False
    
    def can_delete(self, principal: Principal) -> bool:
        entry = self._find_entry_by_principal(principal)
        return entry.can_delete() if entry else False
    
    def can_share(self, principal: Principal) -> bool:
        entry = self._find_entry_by_principal(principal)
        return entry.can_share() if entry else False
    
    def get_principal_roles(self, principal: Principal) -> List[ResourceRole]:
        entry = self._find_entry_by_principal(principal)
        return entry.roles if entry else []
    
    def _find_entry_by_principal(self, principal: Principal) -> Optional[AllowEntry]:
        for entry in self._allow_entries:
            if entry.principal == principal:
                return entry
        return None
    
    def get_all_principals(self) -> List[Principal]:
        return [entry.principal for entry in self._allow_entries]
    
    def get_principals_with_role(self, role: ResourceRole) -> List[Principal]:
        return [
            entry.principal
            for entry in self._allow_entries
            if entry.has_role(role)
        ]
    
    def get_principals_with_full_access(self) -> List[Principal]:
        return self.get_principals_with_role(ResourceRole.FULL_ACCESS)
    
    def get_principals_with_edit_access(self) -> List[Principal]:
        return [
            entry.principal
            for entry in self._allow_entries
            if entry.can_edit()
        ]
    
    def clear_all_permissions(self) -> None:
        self._allow_entries.clear()
        self._updated_at = datetime.now()
    
    def get_permissions_summary(self) -> Dict[str, Any]:
        return {
            'total_entries': len(self._allow_entries),
            'full_access_count': len(self.get_principals_with_full_access()),
            'editor_count': len(self.get_principals_with_role(ResourceRole.EDITOR)),
            'user_count': len(self.get_principals_with_role(ResourceRole.USER)),
            'viewer_count': len(self.get_principals_with_role(ResourceRole.VIEWER)),
            'resource_type': self._resource_type.value,
            'organization_id': str(self._organization_id.value),
            'owner_id': str(self._owner_id.value)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': str(self._id.value),
            'resource_type': self._resource_type.value,
            'resource_id': str(self._resource_id.value),
            'organization_id': str(self._organization_id.value),
            'owner_id': str(self._owner_id.value),
            'allow_entries': [entry.to_dict() for entry in self._allow_entries],
            'created_at': self._created_at,
            'updated_at': self._updated_at
        }