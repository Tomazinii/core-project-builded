# src/infrastructure/database/connection.py (ou database.py)
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool  # ✅ Import correto
from sqlalchemy.orm import declarative_base

logger = logging.getLogger(__name__)

# Base para todos os models
Base = declarative_base()

class DatabaseConnection:
    """
    Gerencia engine e session factory do SQLAlchemy
    
    Singleton que configura:
    - Engine async com pool de conexões
    - SessionFactory para criar sessions
    - Configurações de performance e timeout
    """
    
    _instance: Optional['DatabaseConnection'] = None
    _engine: Optional[AsyncEngine] = None
    _session_factory: Optional[async_sessionmaker[AsyncSession]] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Evita reinicialização
        if self._engine is not None:
            return
    
    def initialize(
        self,
        database_url: str,
        echo: bool = False,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        pool_pre_ping: bool = True
    ):
        """
        Inicializa engine e session factory
        
        Args:
            database_url: URL de conexão (postgresql+asyncpg://...)
            echo: Se True, loga todas as queries SQL
            pool_size: Número de conexões mantidas no pool
            max_overflow: Conexões extras permitidas além do pool_size
            pool_timeout: Tempo de espera por conexão disponível (segundos)
            pool_recycle: Tempo para reciclar conexões antigas (segundos)
            pool_pre_ping: Testa conexão antes de usar (evita conexões mortas)
        """
        
        logger.info(f"Inicializando database connection: {database_url.split('@')[1]}")
        
        # ✅ Para async, use AsyncAdaptedQueuePool ou NullPool
        # Para testes: NullPool (sem pool)
        # Para produção: AsyncAdaptedQueuePool (padrão para async)
        is_test = "test" in database_url
        poolclass = NullPool if is_test else AsyncAdaptedQueuePool
        
        # ✅ Configuração correta para engine assíncrona
        engine_kwargs = {
            "echo": echo,
            "poolclass": poolclass,
            "pool_pre_ping": pool_pre_ping,
            "connect_args": {
                "server_settings": {
                    "application_name": "my_app",
                    "jit": "off",
                },
                "command_timeout": 60,
                "timeout": 10,
            }
        }
        
        # ✅ Adiciona configurações de pool apenas se não for NullPool
        if not is_test:
            engine_kwargs.update({
                "pool_size": pool_size,
                "max_overflow": max_overflow,
                "pool_timeout": pool_timeout,
                "pool_recycle": pool_recycle,
            })
        
        self._engine = create_async_engine(database_url, **engine_kwargs)
        
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
        
        logger.info(
            f"Database connection inicializada: "
            f"pool_size={pool_size if not is_test else 0}, "
            f"max_overflow={max_overflow if not is_test else 0}"
        )
    
    @property
    def engine(self) -> AsyncEngine:
        """Retorna engine"""
        if self._engine is None:
            raise RuntimeError("Database não foi inicializado. Chame initialize() primeiro.")
        return self._engine
    
    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Retorna session factory"""
        if self._session_factory is None:
            raise RuntimeError("Database não foi inicializado. Chame initialize() primeiro.")
        return self._session_factory
    
    async def create_tables(self):
        """Cria todas as tabelas (para desenvolvimento/testes)"""
        logger.info("Criando tabelas...")
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Tabelas criadas")
    
    async def drop_tables(self):
        """Remove todas as tabelas (apenas para testes!)"""
        logger.warning("⚠️  Dropando todas as tabelas!")
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("Tabelas removidas")
    
    async def dispose(self):
        """Fecha todas as conexões do pool"""
        if self._engine:
            logger.info("Fechando conexões do pool...")
            await self._engine.dispose()
            logger.info("Conexões fechadas")
    
    async def health_check(self) -> bool:
        """
        Verifica se o banco está acessível
        
        Returns:
            True se conectou, False caso contrário
        """
        try:
            async with self._engine.connect() as conn:
                from sqlalchemy import text
                await conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Health check falhou: {str(e)}")
            return False


# Singleton global
db_connection = DatabaseConnection()


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    Retorna a session factory
    
    Esta função é usada pelas dependencies do FastAPI
    """
    return db_connection.session_factory


def get_engine() -> AsyncEngine:
    """Retorna o engine"""
    return db_connection.engine