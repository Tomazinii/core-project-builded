# src/presentation/routes/organization_routes.py
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from typing import Annotated

from src.infrastructure.database.deps import get_uow
from src.infrastructure.database.uow.unit_of_work import UnitOfWork
from src.infrastructure.repository.organization_repository_impl import OrganizationRepositoryImpl
from src.domain.entities.organization import Organization, OrganizationId, OrganizationName, OrganizationType, Slug

# Logger para esta rota
logger = logging.getLogger(__name__)

organization_router = APIRouter(prefix="/organizations", tags=["organizations"])


# DTOs/Schemas
class CreateOrganizationRequest(BaseModel):
    """Request schema para criação de organização."""
    name: str = Field(..., min_length=1, max_length=255, description="Nome da organização")
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$", description="Slug único da organização")
    type: str = Field(..., alias="organization_type", description="Tipo da organização")
    
    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if not v.islower():
            raise ValueError("Slug deve conter apenas caracteres minúsculos")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "CEMIG",
                "slug": "cemig",
                "organization_type": "ENERGY"
            }
        }


class CreateOrganizationResponse(BaseModel):
    """Response schema para criação de organização."""
    id: str
    name: str
    slug: str
    organization_type: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "CEMIG",
                "slug": "cemig",
                "organization_type": "ENERGY"
            }
        }


# Service/Use Case
class CreateOrganizationService:
    """Service para encapsular a lógica de criação de organização."""
    
    def __init__(self, repository: OrganizationRepositoryImpl):
        self.repository = repository
        self._logger = logging.getLogger(self.__class__.__name__)
    
    async def execute(self, request: CreateOrganizationRequest) -> Organization:
        """
        Executa a criação de organização com validações de negócio
        
        Args:
            request: Dados da organização a ser criada
            
        Returns:
            Organization: Entidade criada
            
        Raises:
            ValueError: Se slug já existe ou validação falhar
        """
        self._logger.info(f"Criando organização: name={request.name}, slug={request.slug}")
        
        # Validações de negócio
        # existing = await self.repository.find_by_slug(request.slug)
        # if existing:
        #     raise ValueError(f"Organização com slug '{request.slug}' já existe")
        
        try:
            # Criação da entidade
            organization = Organization(
                id=OrganizationId(),
                slug=Slug(request.slug),
                name=OrganizationName(request.name),
                organization_type=OrganizationType(request.type) 
            )
            
            self._logger.debug(f"Entidade criada: {organization}")
            
            # Persiste no banco
            created = await self.repository.create_organization(organization)
            
            self._logger.info(f"Organização criada com sucesso: id={created.id.value}")
            
            return created
            
        except Exception as e:
            self._logger.error(f"Erro ao criar organização: {type(e).__name__}: {str(e)}", exc_info=True)
            raise


# Endpoint
@organization_router.post(
    "",
    response_model=CreateOrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar nova organização",
    description="Cria uma nova organização no sistema",
    responses={
        201: {"description": "Organização criada com sucesso"},
        400: {"description": "Dados inválidos"},
        409: {"description": "Organização com este slug já existe"},
        500: {"description": "Erro interno do servidor"}
    }
)
async def create_organization(
    request: CreateOrganizationRequest,
    uow: Annotated[UnitOfWork, Depends(get_uow)]
) -> CreateOrganizationResponse:
    """
    Cria uma nova organização.
    
    - **name**: Nome completo da organização
    - **slug**: Identificador único em formato slug (apenas letras minúsculas, números e hífens)
    - **organization_type**: Tipo da organização
    """
    logger.info(f"Request recebida: {request.model_dump()}")
    
    try:
        # Instancia repository com a session do UoW
        repo = OrganizationRepositoryImpl(uow.session)
        service = CreateOrganizationService(repo)
        
        # Executa a lógica de negócio
        created_org = await service.execute(request)
        
        # ✅ COMMIT EXPLÍCITO
        await uow.commit()
        logger.info(f"Transação comitada com sucesso: org_id={created_org.id.value}")
        
        # Monta resposta
        response = CreateOrganizationResponse(
            id=created_org.id.value,
            name=created_org.name.value,
            slug=created_org.slug.value,
            organization_type=created_org.organization_type.value
        )
        
        logger.info(f"Response enviada: {response.model_dump()}")
        return response
    
    except ValueError as e:
        # Erro de validação de negócio (ex: slug duplicado)
        logger.warning(f"Erro de validação: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    
    except HTTPException:
        # Re-lança HTTPExceptions já tratadas
        raise
    
    except Exception as e:
        # Erro inesperado - loga TUDO
        logger.error(
            f"Erro inesperado ao criar organização: {type(e).__name__}: {str(e)}",
            exc_info=True  # ✅ Isso vai mostrar o stack trace completo
        )
        
        # Retorna erro genérico pro cliente (não expõe detalhes internos)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar organização. Verifique os logs do servidor."
        )