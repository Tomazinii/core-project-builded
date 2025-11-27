from src.infrastructure.database.database_chatgpt import AsyncSessionLocal


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session






# src/infrastructure/database/dependencies.py
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
    - Rollback automático em caso de exceção
    
    Uso na route:
        @app.post("/organizations")
        async def create_org(uow: UnitOfWork = Depends(get_uow)):
            # UoW já está iniciado, session já existe!
            repo = OrganizationRepositoryImpl(uow.session)
            await repo.create_organization(...)
            await uow.commit()  # Commit explícito
    """
    uow = UnitOfWork(session_factory)
    
    async with uow:  # ✅ Dependency inicia o UoW
        try:
            yield uow  # ✅ Route recebe UoW iniciado
            
            # ⚠️ Após yield: request terminou
            # Se ainda tem transação pendente, avisa e faz rollback
            if uow.session.in_transaction():
                uow._logger.warning(
                    "⚠️ Transação pendente sem commit! "
                    "Esqueceu de chamar await uow.commit()?"
                )
                await uow.rollback()
                
        except Exception as e:
            # ✅ Rollback automático em caso de erro
            uow._logger.error(f"Erro durante request: {e}")
            await uow.rollback()
            raise
        # ✅ Session fechada automaticamente pelo __aexit__ do UoW


# def get_uow() -> UnitOfWork:
#     """
#     Dependency que fornece UnitOfWork
    
#     ✅ RECOMENDADO: Use esta dependency
    
#     Uso:
#         @app.post("/organizations")
#         async def create_org(
#             data: CreateOrgRequest,
#             uow: UnitOfWork = Depends(get_uow)
#         ):
#             async with uow:
#                 repo = OrganizationRepositoryImpl(uow.session)
#                 org = await repo.create_organization(...)
#                 await uow.commit()
#                 return org
#     """
#     session_factory = get_session_factory()
#     return UnitOfWork(session_factory)