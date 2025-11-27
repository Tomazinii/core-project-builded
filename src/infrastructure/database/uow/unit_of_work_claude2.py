# src/infrastructure/database/unit_of_work.py
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

logger = logging.getLogger(__name__)


class UnitOfWork:
    """
    Gerencia transações e lifecycle de sessions
    
    Padrão Unit of Work:
    - Uma session por requisição/operação
    - Commit/rollback centralizado
    - Cleanup automático
    - Context manager seguro
    
    Uso:
        async with UnitOfWork(session_factory) as uow:
            repo = SomeRepository(uow.session)
            await repo.create(...)
            await uow.commit()  # Commit explícito
    """
    
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory
        self._session: Optional[AsyncSession] = None
        self._logger = logger
    
    async def __aenter__(self) -> 'UnitOfWork':
        """Inicia session ao entrar no contexto"""
        self._session = self._session_factory()
        self._logger.debug("UnitOfWork: Session iniciada")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Cleanup ao sair do contexto
        
        Se houve exceção: rollback automático
        Se não houve exceção: fecha session (sem commit automático!)
        """
        try:
            if exc_type is not None:
                # Exceção ocorreu - faz rollback
                self._logger.warning(
                    f"UnitOfWork: Exceção detectada ({exc_type.__name__}), "
                    f"fazendo rollback"
                )
                await self.rollback()
            elif self._session.in_transaction():
                # Session tem transação pendente sem commit
                self._logger.warning(
                    "UnitOfWork: Transação pendente sem commit, fazendo rollback"
                )
                await self.rollback()
        finally:
            # SEMPRE fecha a session
            await self._session.close()
            self._logger.debug("UnitOfWork: Session fechada")
    
    @property
    def session(self) -> AsyncSession:
        """
        Retorna a session atual
        
        Raises:
            RuntimeError: Se UnitOfWork não foi iniciado
        """
        if self._session is None:
            raise RuntimeError(
                "UnitOfWork não foi iniciado. "
                "Use 'async with UnitOfWork(...) as uow:'"
            )
        return self._session
    
    async def commit(self):
        """
        Confirma todas as mudanças pendentes
        
        IMPORTANTE: Commit deve ser explícito no código
        Nunca é feito automaticamente
        """
        try:
            await self._session.commit()
            self._logger.debug("UnitOfWork: Commit realizado")
        except Exception as e:
            self._logger.error(f"UnitOfWork: Erro no commit: {str(e)}")
            await self.rollback()
            raise
    
    async def rollback(self):
        """Desfaz todas as mudanças pendentes"""
        try:
            await self._session.rollback()
            self._logger.debug("UnitOfWork: Rollback realizado")
        except Exception as e:
            self._logger.error(f"UnitOfWork: Erro no rollback: {str(e)}")
            raise
    
    async def flush(self):
        """
        Flush sem commit
        
        Útil para:
        - Validar constraints antes do commit
        - Gerar IDs antes de usar em outras operações
        - Verificar erros de integridade antecipadamente
        """
        await self._session.flush()
        self._logger.debug("UnitOfWork: Flush realizado")
    
    async def refresh(self, instance):
        """Atualiza instância com dados do banco"""
        await self._session.refresh(instance)