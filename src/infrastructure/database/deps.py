# src/infrastructure/database/deps.py (ou dependencies.py)
from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.infrastructure.database.database import get_session_factory
from src.infrastructure.database.uow.unit_of_work import UnitOfWork


async def get_uow(
    session_factory: async_sessionmaker[AsyncSession] = Depends(get_session_factory)
) -> AsyncGenerator[UnitOfWork, None]:
    """
    Dependency que fornece UnitOfWork gerenciado automaticamente
    
    FastAPI cuida do lifecycle completo:
    - Cria session ao iniciar request
    - Fecha session ao finalizar request  
    - Rollback automático em caso de exceção não tratada
    
    ⚠️ IMPORTANTE: A route DEVE fazer commit explícito!
    Se não houver commit, será feito rollback automático.
    
    Uso correto:
        @app.post("/organizations")
        async def create_org(
            request: CreateOrgRequest,
            uow: UnitOfWork = Depends(get_uow)
        ):
            repo = OrganizationRepositoryImpl(uow.session)
            org = await repo.create(request)
            await uow.commit()  # ✅ OBRIGATÓRIO
            return org
    
    Yields:
        UnitOfWork: Instância iniciada e pronta para uso
    """
    uow = UnitOfWork(session_factory)
    
    async with uow:
        try:
            yield uow
            
            # ⚠️ Após yield: request terminou
            # Verifica se esqueceram de fazer commit
            if uow.session.in_transaction():
                uow._logger.warning(
                    "⚠️ Transação pendente detectada! "
                    "Nenhum commit foi feito durante a request. "
                    "Fazendo rollback automático."
                )
                await uow.rollback()
                
        except Exception as e:
            # ✅ Rollback automático em caso de erro
            uow._logger.error(f"Erro durante request, fazendo rollback: {e}")
            await uow.rollback()
            raise
        
        # ✅ Session fechada automaticamente pelo __aexit__ do UoW


# Alias para manter compatibilidade se você já usa esse nome
get_unit_of_work = get_uow