from sqlalchemy.ext.asyncio import AsyncSession

from src.app.infrastructure.repository.organization_repository_impl import (
    OrganizationRepositoryImpl
)


class UnitOfWork:
    """
    Implementação de Unit of Work profissional para SQLAlchemy Async.

    Responsabilidade:
    - Gerenciar ciclo de vida da sessão
    - Controlar commit/rollback
    - Disponibilizar repositórios dentro da transação
    - Suportar uso com 'async with'

    Observação importante:
    - O commit/rollback é centralizado aqui (não deve existir nos repositórios!)
    """

    def __init__(self, session: AsyncSession):
        self.session = session

        # Repositórios lazy-loaded
        self._organizations: OrganizationRepositoryImpl | None = None

    # -----------------------------------------------------------
    # Repositórios expostos pela UoW
    # -----------------------------------------------------------
    @property
    def organizations(self) -> OrganizationRepositoryImpl:
        """
        Repositório de organizações, carregado sob demanda (lazy initialization).
        """
        if self._organizations is None:
            self._organizations = OrganizationRepositoryImpl(self.session)
        return self._organizations

    # -----------------------------------------------------------
    # Controle transacional
    # -----------------------------------------------------------
    async def commit(self):
        """Finaliza a transação."""
        await self.session.commit()

    async def rollback(self):
        """Desfaz alterações em caso de erro."""
        await self.session.rollback()

    async def close(self):
        """Fecha a sessão."""
        await self.session.close()

    # -----------------------------------------------------------
    # Context Manager (async with UoW)
    # -----------------------------------------------------------
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type:  # Se houve erro
            await self.rollback()
        else:
            await self.commit()
        await self.close()


# ===============================================================
# INTEGRAÇÃO COM FASTAPI - Dependency Injection
# ===============================================================

from src.infrastructure.database.deps import get_session

async def get_uow():
    """
    Dependency Injection (FastAPI) para usar a UoW em rotas e use cases.
    
    Uso:
        async def endpoint(uow: UnitOfWork = Depends(get_uow)):
    """
    async for session in get_session():
        async with UnitOfWork(session) as uow:
            yield uow.organizations
