# src/presentation/routes/organization_routes.py
import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from src.infrastructure.database.deps import get_uow
from src.infrastructure.database.uow.unit_of_work import UnitOfWork
from src.presentation.composers.organization_composer import OrganizationComposer
from src.application.usecases.organization_usecase import (
    CreateOrganizationUseCase,
    CreateOrganizationInputDTO,
)
from src.shared.exceptions import (
    DomainException,
)

logger = logging.getLogger(__name__)

organization_router = APIRouter(prefix="/organizations", tags=["organizations"])


class CreateOrganizationRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=3, max_length=63, pattern=r"^[a-z0-9-]+$")
    organization_type: str = Field(..., pattern=r"^(PERSONAL|ENTERPRISE)$")
    
    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if not v.islower():
            raise ValueError("Slug deve estar em minúsculas")
        if v.startswith("-") or v.endswith("-"):
            raise ValueError("Slug não pode iniciar ou terminar com hífen")
        if "--" in v:
            raise ValueError("Slug não pode conter hífens consecutivos")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "CEMIG",
                "slug": "cemig",
                "organization_type": "ENTERPRISE"
            }
        }


class OrganizationResponse(BaseModel):
    id: str
    name: str
    slug: str
    organization_type: str

    class Config:
        from_attributes = True


@organization_router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Organização criada com sucesso"},
        400: {"description": "Dados de entrada inválidos"},
        409: {"description": "Organização com slug já existe"},
        500: {"description": "Erro interno do servidor"},
    }
)
async def create_organization(
    request: CreateOrganizationRequest,
    uow: Annotated[UnitOfWork, Depends(get_uow)],
    use_case: Annotated[CreateOrganizationUseCase, Depends(OrganizationComposer.create_organization)]
) -> OrganizationResponse:
    """
    Cria uma nova organização.
    
    - **name**: Nome da organização (2-100 caracteres)
    - **slug**: Identificador único em formato slug (3-63 caracteres)
    - **organization_type**: Tipo da organização (PERSONAL ou ENTERPRISE)
    """
    try:
        dto = CreateOrganizationInputDTO(
            slug=request.slug,
            name=request.name,
            organization_type=request.organization_type
        )
        
        result = await use_case.execute(dto)
        
        if not result.success:
            await uow.rollback()

            # Caso específico: slug duplicado
            if result.errors and "Slug já está em uso por outra organização" in result.errors:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=result.errors
                )

            # Outros erros de domínio → 400
            if result.errors:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result.errors
                )

            # Fallback → erro não previsto
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao criar organização"
            )

        await uow.commit()
        
        logger.info(
            "Organization created successfully",
            extra={
                "organization_id": result.data["id"],
                "slug": result.data["slug"]
            }
        )
        
        return OrganizationResponse(**result.data)
        
    except HTTPException:
        # Re-levanta HTTPException para que o FastAPI a trate corretamente
        await uow.rollback()
        raise
        
    except DomainException as e:
        await uow.rollback()
        logger.error(f"Domain error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        
    except Exception as e:
        await uow.rollback()
        logger.exception("Unexpected error creating organization")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar organização"
        )