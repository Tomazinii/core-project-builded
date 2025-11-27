from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.organization import (
    Organization,
    OrganizationId,
    Slug,
    OrganizationType
)

class OrganizationRepository(ABC):
    """Contrato de persistência para a entidade Organization."""
    
    @abstractmethod
    def create_organization(self, organization: Organization) -> Organization:
        pass
    
    @abstractmethod
    def update_organization(self, organization: Organization) -> bool:
        pass
    
    @abstractmethod
    def delete_organization(self, organization_id: OrganizationId) -> bool:
        pass
    
    @abstractmethod
    def get_organization_by_id(self, organization_id: OrganizationId) -> Optional[Organization]:
        pass
    
    @abstractmethod
    def get_organization_by_slug(self, slug: Slug) -> Optional[Organization]:
        pass
    
    @abstractmethod
    def list_organizations_by_type(self, organization_type: OrganizationType) -> List[Organization]:
        pass