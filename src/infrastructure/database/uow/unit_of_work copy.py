# src/infrastructure/database/unit_of_work.py
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from typing import Optional

class UnitOfWork:
    """
    Gerencia transações e lifecycle de sessions
    
    Garante:
    - Uma session por requisição
    - Commit/rollback centralizado
    - Cleanup automático
    """
    
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory
        self._session: Optional[AsyncSession] = None
    
    async def __aenter__(self):
        self._session = self._session_factory()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
        await self._session.close()
    
    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("UnitOfWork não foi iniciado")
        return self._session
    
    async def commit(self):
        """Confirma todas as mudanças"""
        await self._session.commit()
    
    async def rollback(self):
        """Desfaz todas as mudanças"""
        await self._session.rollback()

