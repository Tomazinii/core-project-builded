from fastapi import APIRouter, Depends
from uuid import UUID

from src.infrastructure.database.deps import get_session
from src.infrastructure.repository.organization_repository_impl import OrganizationRepositoryImpl

router = APIRouter()




async def create_organization(
    name: str,
    slug: str,
    type: str,
    uow: UnitOfWork = Depends(get_uow)  # Já retorna UoW iniciado
):
    # Não precisa de 'async with' aqui!
    repo = OrganizationRepositoryImpl(uow.session)
    
    org = Organization(...)
    created = await repo.create_organization(org)
    
    await uow.commit()  # Commit explícito
    
    return {"id": created.id.value, ...}









# Exemplo de endpoint usando UnitOfWork
from fastapi import Depends
from src.infrastructure.database.dependencies import get_uow
from src.infrastructure.database.unit_of_work import UnitOfWork
from src.infrastructure.repository.organization_repository_impl import OrganizationRepositoryImpl
from src.domain.entities.organization import Organization, OrganizationId, Slug, OrganizationType, OrganizationName

@app.post("/organizations")
async def create_organization(
    name: str,
    slug: str,
    type: str,
    uow: UnitOfWork = Depends(get_uow)
):
    """Cria organização usando UnitOfWork"""
    async with uow:
        # Cria repositório com session do UoW
        repo = OrganizationRepositoryImpl(uow.session)
        
        # Cria entidade
        org = Organization(
            id=OrganizationId.generate(),  # Método que gera UUID
            slug=Slug(slug),
            name=OrganizationName(name),
            organization_type=OrganizationType(type),
            logo=None,
            acl_id=None
        )
        
        # Salva
        created = await repo.create_organization(org)
        
        # Commit explícito
        await uow.commit()
        
        return {
            "id": created.id.value,
            "slug": created.slug.value,
            "name": created.name.value
        }



async def get_unit_of_work() -> UnitOfWork:
    session_factory = get_session_factory()  # Sua factory
    return UnitOfWork(session_factory)



@router.post("/organizations")
async def create_organization(
    data: CreateOrgRequest,
    uow: UnitOfWork = Depends(get_unit_of_work)
):
    async with uow:
        # Cria repositório com session do UoW
        repo = OrganizationRepositoryImpl(uow.session)
        
        # Cria organização
        org = Organization(...)
        created = await repo.create_organization(org)
        
        # Commit centralizado
        await uow.commit()
        
        return created