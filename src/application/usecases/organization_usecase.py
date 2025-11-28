# =============================================================================
# DTOs DE ENTRADA E SAÍDA
# =============================================================================

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime

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

from src.application.usecases._base import UseCase
from src.domain.repository.organization_repository_interface import OrganizationRepository
from src.domain.entities.organization import (
    Organization,
    OrganizationId,
    Slug,
    OrganizationName,
    Logo,
    ACLId,
    OrganizationType,
)
from src.shared.exceptions import DomainException

class CreateOrganizationUseCase(UseCase[OrganizationRepository, CreateOrganizationInputDTO, OrganizationOutputDTO]):
    """Caso de uso para criar uma nova organização"""
    
    async def execute(self, input_dto: CreateOrganizationInputDTO) -> OrganizationOutputDTO:
        try:
            # Instancia value objects separadamente
            organization_id = OrganizationId()
            slug = Slug(input_dto.slug)
            name = OrganizationName(input_dto.name)
            organization_type = OrganizationType(input_dto.organization_type)
            logo = Logo(input_dto.logo) if input_dto.logo else None
            acl_id = ACLId(input_dto.acl_id) if input_dto.acl_id else None
            
            # Cria a organização
            organization = Organization(
                id=organization_id,
                slug=slug,
                name=name,
                organization_type=organization_type,
                logo=logo,
                acl_id=acl_id
            )
            
            # Valida a entidade e lança exceção se houver erros
            if organization.get_validation_errors():
                raise DomainException(organization.get_validation_errors())
            
            # Validação de negócio: slug único (depende de infraestrutura)
            existing_org = await self._repository.get_organization_by_slug(slug)
            if existing_org:
                raise DomainException(["Slug já está em uso por outra organização"])
            
            # Persiste a organização
            created_org = await self._repository.create_organization(organization)
            
            return OrganizationOutputDTO(
                success=True,
                data={
                    'id': str(created_org.id.value),
                    'slug': created_org.slug.value,
                    'name': created_org.name.value,
                    'organization_type': created_org.organization_type.value,
                    'logo': created_org.logo.value if created_org.logo else None,
                    'acl_id': str(created_org.acl_id.value) if created_org.acl_id else None,
                    'created_at': created_org.created_at.isoformat() if created_org.created_at else None,
                    'updated_at': created_org.updated_at.isoformat() if created_org.updated_at else None
                }
            )
            
        except DomainException as e:
            return OrganizationOutputDTO(
                success=False,
                errors=e.errors
            )
        except Exception as e:
            return OrganizationOutputDTO(
                success=False,
                errors=[f"Erro ao criar organização: {str(e)}"]
            )

class UpdateOrganizationUseCase(UseCase[OrganizationRepository, UpdateOrganizationInputDTO, OrganizationOutputDTO]):
    """Caso de uso para atualizar uma organização"""
    
    async def execute(self, input_dto: UpdateOrganizationInputDTO) -> OrganizationOutputDTO:
        try:
            # Instancia ID
            org_id = OrganizationId(input_dto.id)
            
            # Busca organização existente
            existing_org_dto = await self._repository.get_organization_by_id(org_id)
            
            if not existing_org_dto:
                raise DomainException(["Organização não encontrada"])
            
            # Instancia value objects da organização existente
            existing_id = OrganizationId(existing_org_dto.id)
            existing_slug = Slug(existing_org_dto.slug)
            existing_name = OrganizationName(existing_org_dto.name)
            existing_type = OrganizationType(existing_org_dto.organization_type)
            existing_logo = Logo(existing_org_dto.logo) if existing_org_dto.logo else None
            existing_acl_id = ACLId(existing_org_dto.acl_id) if existing_org_dto.acl_id else None
            
            # Reconstrói a entidade
            organization = Organization(
                id=existing_id,
                slug=existing_slug,
                name=existing_name,
                organization_type=existing_type,
                logo=existing_logo,
                acl_id=existing_acl_id,
                created_at=existing_org_dto.created_at,
                updated_at=existing_org_dto.updated_at
            )
            
            # Aplica as alterações através dos métodos da entidade
            if input_dto.name:
                new_name = OrganizationName(input_dto.name)
                organization.update_name(new_name)
            
            if input_dto.logo:
                new_logo = Logo(input_dto.logo)
                organization.update_logo(new_logo)
            
            if input_dto.acl_id:
                new_acl_id = ACLId(input_dto.acl_id)
                if organization.has_acl():
                    organization.remove_acl()
                organization.assign_acl(new_acl_id)
            
            # Valida a entidade após as alterações
            if organization.get_validation_errors():
                raise DomainException(organization.get_validation_errors())
            
            # Persiste as alterações
            success = await self._repository.update_organization(organization)
            
            if not success:
                raise DomainException(["Falha ao atualizar organização"])
            
            # Busca organização atualizada
            updated_org = await self._repository.get_organization_by_id(org_id)
            
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
            
        except DomainException as e:
            return OrganizationOutputDTO(
                success=False,
                errors=e.errors
            )
        except Exception as e:
            return OrganizationOutputDTO(
                success=False,
                errors=[f"Erro ao atualizar organização: {str(e)}"]
            )

class DeleteOrganizationUseCase(UseCase[OrganizationRepository, DeleteOrganizationInputDTO, OrganizationOutputDTO]):
    """Caso de uso para deletar uma organização"""
    
    async def execute(self, input_dto: DeleteOrganizationInputDTO) -> OrganizationOutputDTO:
        try:
            # Instancia ID
            org_id = OrganizationId(input_dto.id)
            
            # Busca organização
            existing_org = await self._repository.get_organization_by_id(org_id)
            
            if not existing_org:
                raise DomainException(["Organização não encontrada"])
            
            # Deleta organização
            success = await self._repository.delete_organization(org_id)
            
            if not success:
                raise DomainException(["Falha ao deletar organização"])
            
            return OrganizationOutputDTO(
                success=True,
                data={'id': input_dto.id, 'message': 'Organização deletada com sucesso'}
            )
            
        except DomainException as e:
            return OrganizationOutputDTO(
                success=False,
                errors=e.errors
            )
        except Exception as e:
            return OrganizationOutputDTO(
                success=False,
                errors=[f"Erro ao deletar organização: {str(e)}"]
            )

class GetOrganizationByIdUseCase(UseCase[OrganizationRepository, GetOrganizationByIdInputDTO, OrganizationOutputDTO]):
    """Caso de uso para buscar organização por ID"""
    
    async def execute(self, input_dto: GetOrganizationByIdInputDTO) -> OrganizationOutputDTO:
        try:
            # Instancia ID
            org_id = OrganizationId(input_dto.id)
            
            # Busca organização
            organization = await self._repository.get_organization_by_id(org_id)
            
            if not organization:
                raise DomainException(["Organização não encontrada"])
            
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
            
        except DomainException as e:
            return OrganizationOutputDTO(
                success=False,
                errors=e.errors
            )
        except Exception as e:
            return OrganizationOutputDTO(
                success=False,
                errors=[f"Erro ao buscar organização: {str(e)}"]
            )

class GetOrganizationBySlugUseCase(UseCase[OrganizationRepository, GetOrganizationBySlugInputDTO, OrganizationOutputDTO]):
    """Caso de uso para buscar organização por slug"""
    
    async def execute(self, input_dto: GetOrganizationBySlugInputDTO) -> OrganizationOutputDTO:
        try:
            # Instancia Slug
            slug = Slug(input_dto.slug)
            
            # Valida o value object
            if slug.get_validation_errors():
                raise DomainException(slug.get_validation_errors())
            
            # Busca organização
            organization = await self._repository.get_organization_by_slug(slug)
            
            if not organization:
                raise DomainException(["Organização não encontrada"])
            
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
            
        except DomainException as e:
            return OrganizationOutputDTO(
                success=False,
                errors=e.errors
            )
        except Exception as e:
            return OrganizationOutputDTO(
                success=False,
                errors=[f"Erro ao buscar organização: {str(e)}"]
            )

class ListOrganizationsUseCase(UseCase[OrganizationRepository, ListOrganizationsInputDTO, OrganizationOutputDTO]):
    """Caso de uso para listar organizações"""
    
    async def execute(self, input_dto: ListOrganizationsInputDTO) -> OrganizationOutputDTO:
        try:
            if input_dto.organization_type:
                # Instancia tipo de organização
                org_type = OrganizationType(input_dto.organization_type)
                organizations = await self._repository.list_organizations_by_type(org_type)
            else:
                # Lista todos os tipos
                personal_type = OrganizationType.PERSONAL
                enterprise_type = OrganizationType.ENTERPRISE
                
                personal_orgs = await self._repository.list_organizations_by_type(personal_type)
                enterprise_orgs = await self._repository.list_organizations_by_type(enterprise_type)
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
            
        except DomainException as e:
            return OrganizationOutputDTO(
                success=False,
                errors=e.errors
            )
        except Exception as e:
            return OrganizationOutputDTO(
                success=False,
                errors=[f"Erro ao listar organizações: {str(e)}"]
            )

class UpdateOrganizationLogoUseCase(UseCase[OrganizationRepository, UpdateOrganizationLogoInputDTO, OrganizationOutputDTO]):
    """Caso de uso para atualizar logo de uma organização"""
    
    async def execute(self, input_dto: UpdateOrganizationLogoInputDTO) -> OrganizationOutputDTO:
        try:
            # Instancia ID
            org_id = OrganizationId(input_dto.id)
            
            # Busca organização existente
            existing_org_dto = await self._repository.get_organization_by_id(org_id)
            
            if not existing_org_dto:
                raise DomainException(["Organização não encontrada"])
            
            # Instancia value objects da organização existente
            existing_id = OrganizationId(existing_org_dto.id)
            existing_slug = Slug(existing_org_dto.slug)
            existing_name = OrganizationName(existing_org_dto.name)
            existing_type = OrganizationType(existing_org_dto.organization_type)
            existing_logo = Logo(existing_org_dto.logo) if existing_org_dto.logo else None
            existing_acl_id = ACLId(existing_org_dto.acl_id) if existing_org_dto.acl_id else None
            
            # Reconstrói a entidade
            organization = Organization(
                id=existing_id,
                slug=existing_slug,
                name=existing_name,
                organization_type=existing_type,
                logo=existing_logo,
                acl_id=existing_acl_id,
                created_at=existing_org_dto.created_at,
                updated_at=existing_org_dto.updated_at
            )
            
            # Atualiza logo
            new_logo = Logo(input_dto.logo)
            organization.update_logo(new_logo)
            
            # Valida a entidade
            if organization.get_validation_errors():
                raise DomainException(organization.get_validation_errors())
            
            # Persiste
            success = await self._repository.update_organization(organization)
            
            if not success:
                raise DomainException(["Falha ao atualizar logo da organização"])
            
            # Busca organização atualizada
            updated_org = await self._repository.get_organization_by_id(org_id)
            
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
            
        except DomainException as e:
            return OrganizationOutputDTO(
                success=False,
                errors=e.errors
            )
        except Exception as e:
            return OrganizationOutputDTO(
                success=False,
                errors=[f"Erro ao atualizar logo: {str(e)}"]
            )

class UpdateOrganizationNameUseCase(UseCase[OrganizationRepository, UpdateOrganizationNameInputDTO, OrganizationOutputDTO]):
    """Caso de uso para atualizar nome de uma organização"""
    
    async def execute(self, input_dto: UpdateOrganizationNameInputDTO) -> OrganizationOutputDTO:
        try:
            # Instancia ID
            org_id = OrganizationId(input_dto.id)
            
            # Busca organização existente
            existing_org_dto = await self._repository.get_organization_by_id(org_id)
            
            if not existing_org_dto:
                raise DomainException(["Organização não encontrada"])
            
            # Instancia value objects da organização existente
            existing_id = OrganizationId(existing_org_dto.id)
            existing_slug = Slug(existing_org_dto.slug)
            existing_name = OrganizationName(existing_org_dto.name)
            existing_type = OrganizationType(existing_org_dto.organization_type)
            existing_logo = Logo(existing_org_dto.logo) if existing_org_dto.logo else None
            existing_acl_id = ACLId(existing_org_dto.acl_id) if existing_org_dto.acl_id else None
            
            # Reconstrói a entidade
            organization = Organization(
                id=existing_id,
                slug=existing_slug,
                name=existing_name,
                organization_type=existing_type,
                logo=existing_logo,
                acl_id=existing_acl_id,
                created_at=existing_org_dto.created_at,
                updated_at=existing_org_dto.updated_at
            )
            
            # Atualiza nome
            new_name = OrganizationName(input_dto.name)
            organization.update_name(new_name)
            
            # Valida a entidade
            if organization.get_validation_errors():
                raise DomainException(organization.get_validation_errors())
            
            # Persiste
            success = await self._repository.update_organization(organization)
            
            if not success:
                raise DomainException(["Falha ao atualizar nome da organização"])
            
            # Busca organização atualizada
            updated_org = await self._repository.get_organization_by_id(org_id)
            
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
            
        except DomainException as e:
            return OrganizationOutputDTO(
                success=False,
                errors=e.errors
            )
        except Exception as e:
            return OrganizationOutputDTO(
                success=False,
                errors=[f"Erro ao atualizar nome: {str(e)}"]
            )

class UpdateOrganizationTypeUseCase(UseCase[OrganizationRepository, UpdateOrganizationTypeInputDTO, OrganizationOutputDTO]):
    """Caso de uso para atualizar tipo de uma organização"""
    
    async def execute(self, input_dto: UpdateOrganizationTypeInputDTO) -> OrganizationOutputDTO:
        try:
            # Instancia ID e novo tipo
            org_id = OrganizationId(input_dto.id)
            new_type = OrganizationType(input_dto.organization_type)
            
            # Busca organização existente
            existing_org_dto = await self._repository.get_organization_by_id(org_id)
            
            if not existing_org_dto:
                raise DomainException(["Organização não encontrada"])
            
            # Instancia value objects da organização existente
            existing_id = OrganizationId(existing_org_dto.id)
            existing_slug = Slug(existing_org_dto.slug)
            existing_name = OrganizationName(existing_org_dto.name)
            existing_logo = Logo(existing_org_dto.logo) if existing_org_dto.logo else None
            existing_acl_id = ACLId(existing_org_dto.acl_id) if existing_org_dto.acl_id else None
            
            # Reconstrói a entidade com novo tipo
            organization = Organization(
                id=existing_id,
                slug=existing_slug,
                name=existing_name,
                organization_type=new_type,
                logo=existing_logo,
                acl_id=existing_acl_id,
                created_at=existing_org_dto.created_at,
                updated_at=datetime.now()
            )
            
            # Valida a entidade
            if organization.get_validation_errors():
                raise DomainException(organization.get_validation_errors())
            
            # Persiste
            success = await self._repository.update_organization(organization)
            
            if not success:
                raise DomainException(["Falha ao atualizar tipo da organização"])
            
            # Busca organização atualizada
            updated_org = await self._repository.get_organization_by_id(org_id)
            
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
            
        except DomainException as e:
            return OrganizationOutputDTO(
                success=False,
                errors=e.errors
            )
        except Exception as e:
            return OrganizationOutputDTO(
                success=False,
                errors=[f"Erro ao atualizar tipo da organização: {str(e)}"]
            )