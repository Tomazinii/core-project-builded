import logging
from typing import Optional, List, Tuple

from sqlalchemy import select, func, exists, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.domain.entities.organization import (
    Organization,
    OrganizationId,
    Slug,
    OrganizationType,
    OrganizationName,
    Logo,
    ACLId
)

from src.domain.repository.organization_repository_interface import OrganizationRepository
from src.infrastructure.database.models.organization_model import (
    OrganizationModel, 
    OrganizationTypeEnum
)

class OrganizationRepositoryImpl(OrganizationRepository):
    def __init__(self, session: AsyncSession):
        self._session = session
        self._logger = logging.getLogger(self.__class__.__name__)
    
    def _to_model(self, entity: Organization) -> OrganizationModel:
        return OrganizationModel(
            id=entity.id.value,
            slug=entity.slug.value,
            name=entity.name.value,
            type=OrganizationTypeEnum(entity.organization_type.value),
            logo=entity.logo.value if entity.logo else None,
            acl_id=entity.acl_id.value if entity.acl_id else None,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    def _to_entity(self, model: OrganizationModel) -> Organization:
        return Organization(
            id=OrganizationId(model.id),
            slug=Slug(model.slug),
            name=OrganizationName(model.name),
            organization_type=OrganizationType(model.type.value),
            logo=Logo(model.logo) if model.logo else None,
            acl_id=ACLId(model.acl_id) if model.acl_id else None,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    async def create_organization(self, organization: Organization) -> Organization:
        try:
            model = self._to_model(organization)
            self._session.add(model)
            
            await self._session.flush()
            
            self._logger.info(f"Organização criada: {organization.id.value}")
            return self._to_entity(model)
            
        except IntegrityError as e:
            await self._session.rollback() # Boa prática garantir rollback em erro
            error_msg = str(e).lower()
            if "unique" in error_msg and "slug" in error_msg:
                # Otimização: Log warning é melhor que error para validação de negócio
                self._logger.warning(f"Slug duplicado: {organization.slug.value}")
            elif "foreign key" in error_msg:
                 self._logger.warning(f"FK inválida: {organization.acl_id}")
            raise
        except SQLAlchemyError as e:
            self._logger.error(f"Erro DB Create: {e}", exc_info=True)
            raise

    async def update_organization(self, organization: Organization) -> Organization:
        """
        Atualização otimizada.
        """
        try:
            
            stmt = (
                update(OrganizationModel)
                .where(OrganizationModel.id == organization.id.value)
                .values(
                    name=organization.name.value,
                    type=OrganizationTypeEnum(organization.organization_type.value),
                    logo=organization.logo.value if organization.logo else None,
                    acl_id=organization.acl_id.value if organization.acl_id else None,
                    updated_at=organization.updated_at
                )
                .execution_options(synchronize_session="fetch") # Mantém session atualizada
            )
            
            result = await self._session.execute(stmt)
            
            if result.rowcount == 0:
                raise ValueError(f"Organização {organization.id.value} não encontrada")
                
            await self._session.flush()
            
            return organization

        except IntegrityError as e:
            await self._session.rollback()
            self._logger.error(f"Erro integridade Update: {e}")
            raise
        except SQLAlchemyError as e:
            self._logger.error(f"Erro DB Update: {e}")
            raise

    async def delete_organization(self, organization_id: OrganizationId) -> None:
        try:
            stmt = select(OrganizationModel).where(OrganizationModel.id == organization_id.value)
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()

            if not model:
                 raise ValueError(f"Organização {organization_id.value} não encontrada")

            await self._session.delete(model)
            await self._session.flush()
            
        except IntegrityError:
            await self._session.rollback()
            self._logger.error(f"Não é possível deletar {organization_id.value} (FK Constraint)")
            raise
        except Exception as e:
            self._logger.error(f"Erro Delete: {e}")
            raise

    async def get_organization_by_id(self, organization_id: OrganizationId) -> Optional[Organization]:
        model = await self._session.get(OrganizationModel, organization_id.value)
        return self._to_entity(model) if model else None

    async def get_organization_by_slug(self, slug: Slug) -> Optional[Organization]:
        stmt = select(OrganizationModel).where(OrganizationModel.slug == slug.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_organizations_by_type(
        self,
        organization_type: OrganizationType,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[Organization], int]:
        try:
            filter_condition = OrganizationModel.type == OrganizationTypeEnum(organization_type.value)
            
            count_stmt = select(func.count()).select_from(OrganizationModel).where(filter_condition)
            total = (await self._session.execute(count_stmt)).scalar() or 0
            
            if total == 0:
                return [], 0

            stmt = (
                select(OrganizationModel)
                .where(filter_condition)
                .order_by(OrganizationModel.name) # Importante ter índice em (type, name)
                .limit(page_size)
                .offset((page - 1) * page_size)
            )
            
            result = await self._session.execute(stmt)
            models = result.scalars().all()
            
            return [self._to_entity(m) for m in models], total
            
        except SQLAlchemyError as e:
            self._logger.error(f"Erro Listagem: {e}")
            raise

    async def exists_by_slug(self, slug: Slug) -> bool:
        try:
            stmt = select(exists().where(OrganizationModel.slug == slug.value))
            result = await self._session.execute(stmt)
            return result.scalar()
        except SQLAlchemyError as e:
            self._logger.error(f"Erro Exists: {e}")
            raise