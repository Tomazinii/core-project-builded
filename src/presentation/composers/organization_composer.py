# src/application/composers/organization_composer.py
"""
Composers para casos de uso de organização.

Centraliza a composição de dependências para todos os use cases.
Cada método recebe UnitOfWork e retorna o use case configurado.

Pattern: Composition Root + Dependency Injection
"""

from typing import Annotated
from fastapi import Depends

from src.infrastructure.database.deps import get_uow
from src.infrastructure.database.uow.unit_of_work import UnitOfWork
from src.infrastructure.repository.organization_repository_impl import OrganizationRepositoryImpl
from src.application.usecases.organization_usecase import (
    CreateOrganizationUseCase,
    UpdateOrganizationUseCase,
    DeleteOrganizationUseCase,
    GetOrganizationByIdUseCase,
    GetOrganizationBySlugUseCase,
    ListOrganizationsUseCase,
    UpdateOrganizationLogoUseCase,
    UpdateOrganizationNameUseCase,
    UpdateOrganizationTypeUseCase,
)


class OrganizationComposer:
    """
    Composer para casos de uso de organização.
    
    Todos os métodos são FastAPI dependencies que:
    1. Recebem UnitOfWork injetado automaticamente
    2. Criam o repositório com a session do UoW
    3. Retornam o use case configurado
    
    Uso:
        @router.post("/organizations")
        async def create(
            use_case: Annotated[CreateOrganizationUseCase, Depends(OrganizationComposer.create_organization)]
        ):
            ...
    """
    
    # =========================================================================
    # CRUD BÁSICO
    # =========================================================================
    
    @staticmethod
    def create_organization(
        uow: Annotated[UnitOfWork, Depends(get_uow)]
    ) -> CreateOrganizationUseCase:
        """Compõe use case para criação de organização."""
        repository = OrganizationRepositoryImpl(uow.session)
        return CreateOrganizationUseCase(repository)
    
    @staticmethod
    def update_organization(
        uow: Annotated[UnitOfWork, Depends(get_uow)]
    ) -> UpdateOrganizationUseCase:
        """Compõe use case para atualização de organização."""
        repository = OrganizationRepositoryImpl(uow.session)
        return UpdateOrganizationUseCase(repository)
    
    @staticmethod
    def delete_organization(
        uow: Annotated[UnitOfWork, Depends(get_uow)]
    ) -> DeleteOrganizationUseCase:
        """Compõe use case para exclusão de organização."""
        repository = OrganizationRepositoryImpl(uow.session)
        return DeleteOrganizationUseCase(repository)
    
    # =========================================================================
    # CONSULTAS
    # =========================================================================
    
    @staticmethod
    def get_organization_by_id(
        uow: Annotated[UnitOfWork, Depends(get_uow)]
    ) -> GetOrganizationByIdUseCase:
        """Compõe use case para buscar organização por ID."""
        repository = OrganizationRepositoryImpl(uow.session)
        return GetOrganizationByIdUseCase(repository)
    
    @staticmethod
    def get_organization_by_slug(
        uow: Annotated[UnitOfWork, Depends(get_uow)]
    ) -> GetOrganizationBySlugUseCase:
        """Compõe use case para buscar organização por slug."""
        repository = OrganizationRepositoryImpl(uow.session)
        return GetOrganizationBySlugUseCase(repository)
    
    @staticmethod
    def list_organizations(
        uow: Annotated[UnitOfWork, Depends(get_uow)]
    ) -> ListOrganizationsUseCase:
        """Compõe use case para listar organizações."""
        repository = OrganizationRepositoryImpl(uow.session)
        return ListOrganizationsUseCase(repository)
    
    # =========================================================================
    # ATUALIZAÇÕES ESPECÍFICAS
    # =========================================================================
    
    @staticmethod
    def update_organization_logo(
        uow: Annotated[UnitOfWork, Depends(get_uow)]
    ) -> UpdateOrganizationLogoUseCase:
        """Compõe use case para atualizar logo da organização."""
        repository = OrganizationRepositoryImpl(uow.session)
        return UpdateOrganizationLogoUseCase(repository)
    
    @staticmethod
    def update_organization_name(
        uow: Annotated[UnitOfWork, Depends(get_uow)]
    ) -> UpdateOrganizationNameUseCase:
        """Compõe use case para atualizar nome da organização."""
        repository = OrganizationRepositoryImpl(uow.session)
        return UpdateOrganizationNameUseCase(repository)
    
    @staticmethod
    def update_organization_type(
        uow: Annotated[UnitOfWork, Depends(get_uow)]
    ) -> UpdateOrganizationTypeUseCase:
        """Compõe use case para atualizar tipo da organização."""
        repository = OrganizationRepositoryImpl(uow.session)
        return UpdateOrganizationTypeUseCase(repository)