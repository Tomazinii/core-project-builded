# src/infrastructure/database/uow/unit_of_work.py
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class UnitOfWork:
    """
    Gerencia transações e lifecycle de sessions
    
    Garante:
    - Uma session por requisição
    - Commit/rollback centralizado
    - Cleanup automático
    - Logging de operações
    """
    
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory
        self._session: Optional[AsyncSession] = None
        self._logger = logging.getLogger(self.__class__.__name__)
    
    async def __aenter__(self):
        """Inicia a session quando entra no contexto"""
        if self._session is not None:
            raise RuntimeError("UnitOfWork já foi iniciado")
        
        self._session = self._session_factory()
        self._logger.debug("Session criada")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Cleanup ao sair do contexto
        
        - Se houve exceção: rollback automático
        - Sempre fecha a session
        """
        if self._session is None:
            return
        
        try:
            if exc_type is not None:
                self._logger.debug(f"Exceção detectada: {exc_type.__name__}, fazendo rollback")
                await self.rollback()
        finally:
            await self._session.close()
            self._logger.debug("Session fechada")
            self._session = None
    
    @property
    def session(self) -> AsyncSession:
        """
        Retorna a session ativa
        
        Raises:
            RuntimeError: Se UnitOfWork não foi iniciado
        """
        if self._session is None:
            raise RuntimeError(
                "UnitOfWork não foi iniciado. "
                "Use 'async with uow' ou verifique se a dependency foi configurada corretamente."
            )
        return self._session
    
    async def commit(self):
        """
        Confirma todas as mudanças da transação
        
        Raises:
            RuntimeError: Se session não existe
        """
        if self._session is None:
            raise RuntimeError("Não há session ativa para commit")
        
        self._logger.debug("Fazendo commit da transação")
        await self._session.commit()
    
    async def rollback(self):
        """
        Desfaz todas as mudanças da transação
        
        Raises:
            RuntimeError: Se session não existe
        """
        if self._session is None:
            raise RuntimeError("Não há session ativa para rollback")
        
        self._logger.debug("Fazendo rollback da transação")
        await self._session.rollback()
    
    async def flush(self):
        """
        Envia mudanças para o banco sem fazer commit
        
        Útil para obter IDs gerados antes do commit final
        """
        if self._session is None:
            raise RuntimeError("Não há session ativa para flush")
        
        self._logger.debug("Fazendo flush da session")
        await self._session.flush()
    
    async def refresh(self, instance):
        """
        Atualiza uma instância com dados frescos do banco
        
        Args:
            instance: Entidade a ser atualizada
        """
        if self._session is None:
            raise RuntimeError("Não há session ativa para refresh")
        
        await self._session.refresh(instance)