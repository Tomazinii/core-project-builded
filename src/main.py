# src/main.py
import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src import config
from src.infrastructure.database.database import db_connection
from src.presentation.routes.organization_routes import organization_router

# ✅ Configuração de logging ANTES de tudo
logging.basicConfig(
    level=logging.DEBUG,  # Mude para INFO em produção
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

DATABASE_URL = (
    f"postgresql+asyncpg://{config.DB_USER}:{config.DB_PASSWORD}"
    f"@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
)

# Configurações
class Settings:
    database_url: str = DATABASE_URL
    database_echo: bool = False  # Mude para True para ver queries SQL
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_timeout: int = 30
    database_pool_recycle: int = 3600
    
settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia lifecycle da aplicação"""
    # Startup
    logger.info("🚀 Iniciando aplicação...")
    
    try:
        # Inicializa database
        db_connection.initialize(
            database_url=settings.database_url,
            echo=settings.database_echo,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_timeout=settings.database_pool_timeout,
            pool_recycle=settings.database_pool_recycle,
        )
        
        # Health check
        if await db_connection.health_check():
            logger.info("✅ Database conectado")
        else:
            logger.error("❌ Falha ao conectar no database")
            raise RuntimeError("Database não está acessível")
        
    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {e}", exc_info=True)
        raise
    
    yield  # Aplicação roda aqui
    
    # Shutdown
    logger.info("🛑 Encerrando aplicação...")
    await db_connection.dispose()
    logger.info("✅ Conexões fechadas")


# Cria app
app = FastAPI(
    title="Application Core",
    description="Secure and scalable account management system",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(
    organization_router,
    prefix="/api/v1/assistant_router",
    tags=["Organization"]
)


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"  # ✅ Mostra logs detalhados
    )