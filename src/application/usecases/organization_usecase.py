# =============================================================================
# DTOs DE ENTRADA E SAÍDA
# =============================================================================

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from src.domain.entities.organization import (
    OrganizationType,
)

@dataclass(frozen=True)
class CreateOrganizationInputDTO:
    slug: str
    name: str
    organization_type: str
    logo: Optional[str] = None
    acl_id: Optional[str] = None

@dataclass(frozen=True)
class UpdateOrganizationInputDTO:
    id: str
    name: Optional[str] = None
    logo: Optional[str] = None
    acl_id: Optional[str] = None

@dataclass(frozen=True)
class DeleteOrganizationInputDTO:
    id: str

@dataclass(frozen=True)
class GetOrganizationByIdInputDTO:
    id: str

@dataclass(frozen=True)
class GetOrganizationBySlugInputDTO:
    slug: str

@dataclass(frozen=True)
class ListOrganizationsInputDTO:
    organization_type: Optional[str] = None

@dataclass(frozen=True)
class UpdateOrganizationLogoInputDTO:
    id: str
    logo: str

@dataclass(frozen=True)
class UpdateOrganizationNameInputDTO:
    id: str
    name: str

@dataclass(frozen=True)
class UpdateOrganizationTypeInputDTO:
    id: str
    organization_type: str

@dataclass(frozen=True)
class OrganizationOutputDTO:
    success: bool
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None

# =============================================================================
# USE CASES
# =============================================================================

from src.application.use_cases._base import UseCase
from src.domain.repositories.organization_repository_interface import OrganizationRepository
from src.domain.entities.organization import (
    Organization,
    OrganizationId,
    Slug,
    OrganizationName,
    Logo,
    ACLId,
)

class CreateOrganizationUseCase(UseCase[OrganizationRepository, CreateOrganizationInputDTO, OrganizationOutputDTO]):
    """Caso de uso para criar uma nova organização"""
    
    async def execute(self, input_dto: CreateOrganizationInputDTO) -> OrganizationOutputDTO:
        try:
            organization_type = OrganizationType(input_dto.organization_type)
        except ValueError:
            return self._create_error_output([f"Tipo de organização inválido: {input_dto.organization_type}"])
        
        try:
            slug = Slug(input_dto.slug)
            name = OrganizationName(input_dto.name)
            logo = Logo(input_dto.logo) if input_dto.logo else None
            acl_id = ACLId(input_dto.acl_id) if input_dto.acl_id else None
            
            organization_id = OrganizationId.generate()
            
            organization = Organization(
                id=organization_id,
                slug=slug,
                name=name,
                organization_type=organization_type,
                logo=logo,
                acl_id=acl_id
            )
            
            errors = self._get_errors(organization)
            if errors:
                return self._create_error_output(errors)
            
            existing_org = self.repository.get_organization_by_slug(slug)
            if existing_org:
                return self._create_error_output(["Slug já está em uso por outra organização"])
            
            created_org = self.repository.create_organization(organization)
            
            return OrganizationOutputDTO(
                success=True,
                data={
                    'id': str(created_org.id),
                    'slug': created_org.slug,
                    'name': created_org.name,
                    'organization_type': created_org.organization_type,
                    'logo': created_org.logo,
                    'acl_id': created_org.acl_id,
                    'created_at': created_org.created_at.isoformat() if created_org.created_at else None,
                    'updated_at': created_org.updated_at.isoformat() if created_org.updated_at else None
                }
            )
            
        except ValueError as e:
            return self._create_error_output([str(e)])
        except Exception as e:
            return self._create_error_output([f"Erro ao criar organização: {str(e)}"])

class UpdateOrganizationUseCase(UseCase[OrganizationRepository, UpdateOrganizationInputDTO, OrganizationOutputDTO]):
    """Caso de uso para atualizar uma organização"""
    
    async def execute(self, input_dto: UpdateOrganizationInputDTO) -> OrganizationOutputDTO:
        organization_id = self._validate_uuid(input_dto.id, "ID da organização")
        if not organization_id:
            return self._create_error_output(["ID da organização inválido"])
        
        try:
            org_id = OrganizationId(organization_id)
            existing_org_dto = self.repository.get_organization_by_id(org_id)
            
            if not existing_org_dto:
                return self._create_error_output(["Organização não encontrada"])
            
            try:
                organization_type = OrganizationType(existing_org_dto.organization_type)
            except ValueError:
                return self._create_error_output([f"Tipo de organização inválido: {existing_org_dto.organization_type}"])
            
            organization = Organization(
                id=OrganizationId(existing_org_dto.id),
                slug=Slug(existing_org_dto.slug),
                name=OrganizationName(existing_org_dto.name),
                organization_type=organization_type,
                logo=Logo(existing_org_dto.logo) if existing_org_dto.logo else None,
                acl_id=ACLId(existing_org_dto.acl_id) if existing_org_dto.acl_id else None,
                created_at=existing_org_dto.created_at,
                updated_at=existing_org_dto.updated_at
            )
            
            if input_dto.name:
                try:
                    new_name = OrganizationName(input_dto.name)
                    organization.update_name(new_name)
                except ValueError as e:
                    return self._create_error_output([str(e)])
            
            if input_dto.logo:
                try:
                    new_logo = Logo(input_dto.logo)
                    organization.update_logo(new_logo)
                except ValueError as e:
                    return self._create_error_output([str(e)])
            
            if input_dto.acl_id:
                try:
                    new_acl_id = ACLId(input_dto.acl_id)
                    if organization.has_acl():
                        organization.remove_acl()
                    organization.assign_acl(new_acl_id)
                except ValueError as e:
                    return self._create_error_output([str(e)])
            
            errors = self._get_errors(organization)
            if errors:
                return self._create_error_output(errors)
            
            success = self.repository.update_organization(organization)
            
            if not success:
                return self._create_error_output(["Falha ao atualizar organização"])
            
            updated_org = self.repository.get_organization_by_id(org_id)
            
            return OrganizationOutputDTO(
                success=True,
                data={
                    'id': updated_org.id,
                    'slug': updated_org.slug,
                    'name': updated_org.name,
                    'organization_type': updated_org.organization_type,
                    'logo': updated_org.logo,
                    'acl_id': updated_org.acl_id,
                    'created_at': updated_org.created_at.isoformat() if updated_org.created_at else None,
                    'updated_at': updated_org.updated_at.isoformat() if updated_org.updated_at else None
                }
            )
            
        except Exception as e:
            return self._create_error_output([f"Erro ao atualizar organização: {str(e)}"])

class DeleteOrganizationUseCase(UseCase[OrganizationRepository, DeleteOrganizationInputDTO, OrganizationOutputDTO]):
    """Caso de uso para deletar uma organização"""
    
    async def execute(self, input_dto: DeleteOrganizationInputDTO) -> OrganizationOutputDTO:
        organization_id = self._validate_uuid(input_dto.id, "ID da organização")
        if not organization_id:
            return self._create_error_output(["ID da organização inválido"])
        
        try:
            org_id = OrganizationId(organization_id)
            existing_org = self.repository.get_organization_by_id(org_id)
            
            if not existing_org:
                return self._create_error_output(["Organização não encontrada"])
            
            success = self.repository.delete_organization(org_id)
            
            if not success:
                return self._create_error_output(["Falha ao deletar organização"])
            
            return OrganizationOutputDTO(
                success=True,
                data={'id': input_dto.id, 'message': 'Organização deletada com sucesso'}
            )
            
        except Exception as e:
            return self._create_error_output([f"Erro ao deletar organização: {str(e)}"])

class GetOrganizationByIdUseCase(UseCase[OrganizationRepository, GetOrganizationByIdInputDTO, OrganizationOutputDTO]):
    """Caso de uso para buscar organização por ID"""
    
    async def execute(self, input_dto: GetOrganizationByIdInputDTO) -> OrganizationOutputDTO:
        organization_id = self._validate_uuid(input_dto.id, "ID da organização")
        if not organization_id:
            return self._create_error_output(["ID da organização inválido"])
        
        try:
            org_id = OrganizationId(organization_id)
            organization = self.repository.get_organization_by_id(org_id)
            
            if not organization:
                return self._create_error_output(["Organização não encontrada"])
            
            return OrganizationOutputDTO(
                success=True,
                data={
                    'id': organization.id,
                    'slug': organization.slug,
                    'name': organization.name,
                    'organization_type': organization.organization_type,
                    'logo': organization.logo,
                    'acl_id': organization.acl_id,
                    'created_at': organization.created_at.isoformat() if organization.created_at else None,
                    'updated_at': organization.updated_at.isoformat() if organization.updated_at else None
                }
            )
            
        except Exception as e:
            return self._create_error_output([f"Erro ao buscar organização: {str(e)}"])

class GetOrganizationBySlugUseCase(UseCase[OrganizationRepository, GetOrganizationBySlugInputDTO, OrganizationOutputDTO]):
    """Caso de uso para buscar organização por slug"""
    
    async def execute(self, input_dto: GetOrganizationBySlugInputDTO) -> OrganizationOutputDTO:
        try:
            slug = Slug(input_dto.slug)
            organization = self.repository.get_organization_by_slug(slug)
            
            if not organization:
                return self._create_error_output(["Organização não encontrada"])
            
            return OrganizationOutputDTO(
                success=True,
                data={
                    'id': organization.id,
                    'slug': organization.slug,
                    'name': organization.name,
                    'organization_type': organization.organization_type,
                    'logo': organization.logo,
                    'acl_id': organization.acl_id,
                    'created_at': organization.created_at.isoformat() if organization.created_at else None,
                    'updated_at': organization.updated_at.isoformat() if organization.updated_at else None
                }
            )
            
        except ValueError as e:
            return self._create_error_output([str(e)])
        except Exception as e:
            return self._create_error_output([f"Erro ao buscar organização: {str(e)}"])

class ListOrganizationsUseCase(UseCase[OrganizationRepository, ListOrganizationsInputDTO, OrganizationOutputDTO]):
    """Caso de uso para listar organizações"""
    
    async def execute(self, input_dto: ListOrganizationsInputDTO) -> OrganizationOutputDTO:
        try:
            if input_dto.organization_type:
                try:
                    org_type = OrganizationType(input_dto.organization_type)
                    organizations = self.repository.list_organizations_by_type(org_type)
                except ValueError:
                    return self._create_error_output([f"Tipo de organização inválido: {input_dto.organization_type}"])
            else:
                personal_orgs = self.repository.list_organizations_by_type(OrganizationType.PERSONAL)
                enterprise_orgs = self.repository.list_organizations_by_type(OrganizationType.ENTERPRISE)
                organizations = personal_orgs + enterprise_orgs
            
            organizations_data = [
                {
                    'id': org.id,
                    'slug': org.slug,
                    'name': org.name,
                    'organization_type': org.organization_type,
                    'logo': org.logo,
                    'acl_id': org.acl_id,
                    'created_at': org.created_at.isoformat() if org.created_at else None,
                    'updated_at': org.updated_at.isoformat() if org.updated_at else None
                }
                for org in organizations
            ]
            
            return OrganizationOutputDTO(
                success=True,
                data={
                    'organizations': organizations_data,
                    'total': len(organizations_data)
                }
            )
            
        except Exception as e:
            return self._create_error_output([f"Erro ao listar organizações: {str(e)}"])

class UpdateOrganizationLogoUseCase(UseCase[OrganizationRepository, UpdateOrganizationLogoInputDTO, OrganizationOutputDTO]):
    """Caso de uso para atualizar logo de uma organização"""
    
    async def execute(self, input_dto: UpdateOrganizationLogoInputDTO) -> OrganizationOutputDTO:
        organization_id = self._validate_uuid(input_dto.id, "ID da organização")
        if not organization_id:
            return self._create_error_output(["ID da organização inválido"])
        
        try:
            org_id = OrganizationId(organization_id)
            existing_org_dto = self.repository.get_organization_by_id(org_id)
            
            if not existing_org_dto:
                return self._create_error_output(["Organização não encontrada"])
            
            try:
                organization_type = OrganizationType(existing_org_dto.organization_type)
            except ValueError:
                return self._create_error_output([f"Tipo de organização inválido: {existing_org_dto.organization_type}"])
            
            organization = Organization(
                id=OrganizationId(existing_org_dto.id),
                slug=Slug(existing_org_dto.slug),
                name=OrganizationName(existing_org_dto.name),
                organization_type=organization_type,
                logo=Logo(existing_org_dto.logo) if existing_org_dto.logo else None,
                acl_id=ACLId(existing_org_dto.acl_id) if existing_org_dto.acl_id else None,
                created_at=existing_org_dto.created_at,
                updated_at=existing_org_dto.updated_at
            )
            
            try:
                new_logo = Logo(input_dto.logo)
                organization.update_logo(new_logo)
            except ValueError as e:
                return self._create_error_output([str(e)])
            
            errors = self._get_errors(organization)
            if errors:
                return self._create_error_output(errors)
            
            success = self.repository.update_organization(organization)
            
            if not success:
                return self._create_error_output(["Falha ao atualizar logo da organização"])
            
            updated_org = self.repository.get_organization_by_id(org_id)
            
            return OrganizationOutputDTO(
                success=True,
                data={
                    'id': updated_org.id,
                    'slug': updated_org.slug,
                    'name': updated_org.name,
                    'organization_type': updated_org.organization_type,
                    'logo': updated_org.logo,
                    'acl_id': updated_org.acl_id,
                    'created_at': updated_org.created_at.isoformat() if updated_org.created_at else None,
                    'updated_at': updated_org.updated_at.isoformat() if updated_org.updated_at else None
                }
            )
            
        except Exception as e:
            return self._create_error_output([f"Erro ao atualizar logo: {str(e)}"])

class UpdateOrganizationNameUseCase(UseCase[OrganizationRepository, UpdateOrganizationNameInputDTO, OrganizationOutputDTO]):
    """Caso de uso para atualizar nome de uma organização"""
    
    async def execute(self, input_dto: UpdateOrganizationNameInputDTO) -> OrganizationOutputDTO:
        organization_id = self._validate_uuid(input_dto.id, "ID da organização")
        if not organization_id:
            return self._create_error_output(["ID da organização inválido"])
        
        try:
            org_id = OrganizationId(organization_id)
            existing_org_dto = self.repository.get_organization_by_id(org_id)
            
            if not existing_org_dto:
                return self._create_error_output(["Organização não encontrada"])
            
            try:
                organization_type = OrganizationType(existing_org_dto.organization_type)
            except ValueError:
                return self._create_error_output([f"Tipo de organização inválido: {existing_org_dto.organization_type}"])
            
            organization = Organization(
                id=OrganizationId(existing_org_dto.id),
                slug=Slug(existing_org_dto.slug),
                name=OrganizationName(existing_org_dto.name),
                organization_type=organization_type,
                logo=Logo(existing_org_dto.logo) if existing_org_dto.logo else None,
                acl_id=ACLId(existing_org_dto.acl_id) if existing_org_dto.acl_id else None,
                created_at=existing_org_dto.created_at,
                updated_at=existing_org_dto.updated_at
            )
            
            try:
                new_name = OrganizationName(input_dto.name)
                organization.update_name(new_name)
            except ValueError as e:
                return self._create_error_output([str(e)])
            
            errors = self._get_errors(organization)
            if errors:
                return self._create_error_output(errors)
            
            success = self.repository.update_organization(organization)
            
            if not success:
                return self._create_error_output(["Falha ao atualizar nome da organização"])
            
            updated_org = self.repository.get_organization_by_id(org_id)
            
            return OrganizationOutputDTO(
                success=True,
                data={
                    'id': updated_org.id,
                    'slug': updated_org.slug,
                    'name': updated_org.name,
                    'organization_type': updated_org.organization_type,
                    'logo': updated_org.logo,
                    'acl_id': updated_org.acl_id,
                    'created_at': updated_org.created_at.isoformat() if updated_org.created_at else None,
                    'updated_at': updated_org.updated_at.isoformat() if updated_org.updated_at else None
                }
            )
            
        except Exception as e:
            return self._create_error_output([f"Erro ao atualizar nome: {str(e)}"])

class UpdateOrganizationTypeUseCase(UseCase[OrganizationRepository, UpdateOrganizationTypeInputDTO, OrganizationOutputDTO]):
    """Caso de uso para atualizar tipo de uma organização"""
    
    async def execute(self, input_dto: UpdateOrganizationTypeInputDTO) -> OrganizationOutputDTO:
        organization_id = self._validate_uuid(input_dto.id, "ID da organização")
        if not organization_id:
            return self._create_error_output(["ID da organização inválido"])
        
        try:
            new_type = OrganizationType(input_dto.organization_type)
        except ValueError:
            return self._create_error_output([f"Tipo de organização inválido: {input_dto.organization_type}"])
        
        try:
            org_id = OrganizationId(organization_id)
            existing_org_dto = self.repository.get_organization_by_id(org_id)
            
            if not existing_org_dto:
                return self._create_error_output(["Organização não encontrada"])
            
            organization = Organization(
                id=OrganizationId(existing_org_dto.id),
                slug=Slug(existing_org_dto.slug),
                name=OrganizationName(existing_org_dto.name),
                organization_type=new_type,
                logo=Logo(existing_org_dto.logo) if existing_org_dto.logo else None,
                acl_id=ACLId(existing_org_dto.acl_id) if existing_org_dto.acl_id else None,
                created_at=existing_org_dto.created_at,
                updated_at=datetime.now()
            )
            
            errors = self._get_errors(organization)
            if errors:
                return self._create_error_output(errors)
            
            success = self.repository.update_organization(organization)
            
            if not success:
                return self._create_error_output(["Falha ao atualizar tipo da organização"])
            
            updated_org = self.repository.get_organization_by_id(org_id)
            
            return OrganizationOutputDTO(
                success=True,
                data={
                    'id': updated_org.id,
                    'slug': updated_org.slug,
                    'name': updated_org.name,
                    'organization_type': updated_org.organization_type,
                    'logo': updated_org.logo,
                    'acl_id': updated_org.acl_id,
                    'created_at': updated_org.created_at.isoformat() if updated_org.created_at else None,
                    'updated_at': updated_org.updated_at.isoformat() if updated_org.updated_at else None
                }
            )
            
        except Exception as e:
            return self._create_error_output([f"Erro ao atualizar tipo da organização: {str(e)}"])