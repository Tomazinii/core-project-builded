import logging
from typing import Optional, List, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
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
    """
    Implementação assíncrona do OrganizationRepository usando SQLAlchemy
    
    Features:
    - Operações 100% assíncronas para alta concorrência
    - Session management seguro (session por operação)
    - Queries otimizadas com índices
    - Tratamento robusto e específico de erros
    - Paginação para listas
    - Logging estruturado
    
    Thread-Safety:
    - Usa session_factory para criar sessions isoladas
    - Cada operação tem sua própria session
    - Seguro para milhares de requisições concorrentes
    """
    
    def __init__(self, session: AsyncSession):
        """
        Args:
            session: AsyncSession gerenciada por UnitOfWork
                    Essa session é controlada externamente (commit/rollback)
        """
        self._session = session
        self._logger = logging.getLogger(self.__class__.__name__)
    
    def _to_model(self, entity: Organization) -> OrganizationModel:
        """Converte Entity para Model (persistência)"""
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
        """Converte Model para Entity (domínio)"""
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
        """
        Cria uma nova organização
        
        Performance:
        - INSERT direto sem SELECT prévio
        - Flush para validação de constraints
        - Commit controlado externamente (UnitOfWork)
        
        Returns:
            Organization criada com ID confirmado
        
        Raises:
            IntegrityError: Se slug já existe ou ACL_ID inválido
            SQLAlchemyError: Outros erros de banco
        """
        try:
            model = self._to_model(organization)
            self._session.add(model)
            
            # Flush valida constraints e triggers sem fazer commit
            await self._session.flush()
            
            # Refresh para pegar valores gerados pelo banco (se houver)
            await self._session.refresh(model)
            
            self._logger.info(
                f"Organização criada: id={organization.id.value}, "
                f"slug={organization.slug.value}"
            )
            
            return self._to_entity(model)
            
        except IntegrityError as e:
            error_msg = str(e).lower()
            
            if "unique" in error_msg and "slug" in error_msg:
                self._logger.warning(
                    f"Tentativa de criar organização com slug duplicado: "
                    f"{organization.slug.value}"
                )
            elif "foreign key" in error_msg and "acl_id" in error_msg:
                self._logger.error(
                    f"ACL_ID inválido: {organization.acl_id.value if organization.acl_id else None}"
                )
            else:
                self._logger.error(
                    f"Erro de integridade ao criar organização: {str(e)}",
                    exc_info=True
                )
            raise
                
        except SQLAlchemyError as e:
            self._logger.error(
                f"Erro ao criar organização: {str(e)}",
                exc_info=True
            )
            raise
    
    async def update_organization(self, organization: Organization) -> Organization:
        """
        Atualiza uma organização existente
        
        Performance:
        - Usa get() para buscar por PK (mais rápido)
        - UPDATE in-place
        - Flush para validação
        
        Returns:
            Organization atualizada
        
        Raises:
            ValueError: Se não encontrar a organização
            IntegrityError: Se ACL_ID inválido
            SQLAlchemyError: Outros erros
        """
        try:
            # get() é mais eficiente para primary key
            existing = await self._session.get(
                OrganizationModel, 
                organization.id.value
            )
            
            if not existing:
                raise ValueError(
                    f"Organização {organization.id.value} não encontrada"
                )
            
            # Atualiza campos
            existing.name = organization.name.value
            existing.type = OrganizationTypeEnum(organization.organization_type.value)
            existing.logo = organization.logo.value if organization.logo else None
            existing.acl_id = organization.acl_id.value if organization.acl_id else None
            existing.updated_at = organization.updated_at
            
            await self._session.flush()
            
            self._logger.info(f"Organização atualizada: {organization.id.value}")
            
            return self._to_entity(existing)
            
        except ValueError:
            raise
            
        except IntegrityError as e:
            error_msg = str(e).lower()
            
            if "foreign key" in error_msg:
                self._logger.error(f"ACL_ID inválido na atualização: {str(e)}")
            else:
                self._logger.error(f"Erro de integridade na atualização: {str(e)}")
            raise
                
        except SQLAlchemyError as e:
            self._logger.error(f"Erro ao atualizar organização: {str(e)}")
            raise
    
    async def delete_organization(self, organization_id: OrganizationId) -> None:
        """
        Remove organização
        
        Performance:
        - Usa get() para PK
        - DELETE direto
        
        Raises:
            ValueError: Se não encontrar a organização
            IntegrityError: Se houver dependências
            SQLAlchemyError: Outros erros
        """
        try:
            existing = await self._session.get(
                OrganizationModel,
                organization_id.value
            )
            
            if not existing:
                raise ValueError(
                    f"Organização {organization_id.value} não encontrada"
                )
            
            await self._session.delete(existing)
            await self._session.flush()
            
            self._logger.info(f"Organização deletada: {organization_id.value}")
            
        except ValueError:
            raise
            
        except IntegrityError as e:
            self._logger.error(
                f"Erro ao deletar organização (dependências?): {str(e)}"
            )
            raise
            
        except SQLAlchemyError as e:
            self._logger.error(f"Erro ao deletar organização: {str(e)}")
            raise
    
    async def get_organization_by_id(
        self, 
        organization_id: OrganizationId
    ) -> Optional[Organization]:
        """
        Busca organização por ID
        
        Performance:
        - get() usa cache de session (identity map)
        - Acesso O(1) se já carregado na session
        - Acesso por índice primário se não estiver em cache
        
        Returns:
            Organization se encontrada, None caso contrário
        
        Raises:
            SQLAlchemyError: Erros de banco de dados
        """
        try:
            model = await self._session.get(
                OrganizationModel,
                organization_id.value
            )
            
            if not model:
                self._logger.debug(
                    f"Organização não encontrada: {organization_id.value}"
                )
                return None
            
            return self._to_entity(model)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Erro ao buscar organização por ID: {str(e)}")
            raise
    
    async def get_organization_by_slug(self, slug: Slug) -> Optional[Organization]:
        """
        Busca organização por slug
        
        Performance:
        - Usa índice único em slug (O(log n))
        - scalar_one_or_none() mais eficiente que first()
        
        Raises:
            SQLAlchemyError: Erros de banco de dados
        """
        try:
            stmt = select(OrganizationModel).where(
                OrganizationModel.slug == slug.value
            )
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()
            
            if not model:
                self._logger.debug(f"Organização não encontrada: slug={slug.value}")
                return None
            
            return self._to_entity(model)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Erro ao buscar organização por slug: {str(e)}")
            raise
    
    async def list_organizations_by_type(
        self,
        organization_type: OrganizationType,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[Organization], int]:
        """
        Lista organizações por tipo com paginação
        
        Performance:
        - Usa índice em type (se existir)
        - Query otimizada para count
        - LIMIT/OFFSET para paginação
        
        Args:
            organization_type: Tipo da organização
            page: Número da página (inicia em 1)
            page_size: Itens por página
        
        Returns:
            (lista de organizações, total de registros)
        
        Raises:
            SQLAlchemyError: Erros de banco de dados
        """
        try:
            # Query base
            base_where = OrganizationModel.type == OrganizationTypeEnum(
                organization_type.value
            )
            
            # Count total (mais eficiente que subquery)
            count_stmt = select(func.count()).select_from(
                OrganizationModel
            ).where(base_where)
            
            total_result = await self._session.execute(count_stmt)
            total = total_result.scalar()
            
            # Query paginada
            stmt = (
                select(OrganizationModel)
                .where(base_where)
                .order_by(OrganizationModel.name)
                .limit(page_size)
                .offset((page - 1) * page_size)
            )
            
            result = await self._session.execute(stmt)
            models = result.scalars().all()
            
            organizations = [self._to_entity(model) for model in models]
            
            self._logger.debug(
                f"Listadas {len(organizations)} organizações do tipo "
                f"{organization_type.value} (página {page}/{(total + page_size - 1) // page_size})"
            )
            
            return organizations, total
            
        except SQLAlchemyError as e:
            self._logger.error(f"Erro ao listar organizações: {str(e)}")
            raise
    
    async def exists_by_slug(self, slug: Slug) -> bool:
        """
        Verifica se organização existe pelo slug
        
        Performance:
        - EXISTS é mais rápido que COUNT ou SELECT
        - Usa índice único
        
        Returns:
            True se existe, False caso contrário
        
        Raises:
            SQLAlchemyError: Erros de banco de dados
        """
        try:
            stmt = select(
                exists().where(OrganizationModel.slug == slug.value)
            )
            result = await self._session.execute(stmt)
            return result.scalar()
            
        except SQLAlchemyError as e:
            self._logger.error(f"Erro ao verificar existência de slug: {str(e)}")
            raise