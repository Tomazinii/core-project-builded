import os
from pathlib import Path


from dotenv import load_dotenv

load_dotenv()


# =============================================================================
# CONFIGURAÇÕES GERAIS DA APLICAÇÃO
# =============================================================================

# Informações básicas da aplicação
APP_NAME = os.getenv("APP_NAME", "MyApplication")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "Minha aplicação Python")
APP_DEBUG = os.getenv("APP_DEBUG", "True").lower() == "true"
APP_ENVIRONMENT = os.getenv("APP_ENVIRONMENT", "development")


# Informações sobre GCP
GCP_BUCKET_NAME=os.getenv("GCP_BUCKET_NAME", "knowledge_assistant_bucket_core")




# Configurações do servidor
SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
SERVER_RELOAD = os.getenv("SERVER_RELOAD", "True").lower() == "true"
SERVER_WORKERS = int(os.getenv("SERVER_WORKERS", "1"))


# =============================================================================
# CONFIGURAÇÕES DE DATA INGESTION SERVICE
# =============================================================================
DATA_INGESTION_API_URL = os.getenv("DATA_INGESTION_API_URL", "http://host.docker.internal:5000")

# =============================================================================
# CONFIGURAÇÕES DE BANCO DE DADOS
# =============================================================================

# Credenciais do PostgreSQL
DB_NAME = os.getenv("POSTGRES_DB", "mydatabase")
DB_USER = os.getenv("POSTGRES_USER", "myuser")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "mypassword")
DB_HOST = os.getenv("POSTGRES_HOST", "host.docker.internal")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5434"))

# URL de conexão completa
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# =============================================================================
# CONFIGURAÇÕES AVANÇADAS DE CONEXÃO
# =============================================================================

DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))

DB_MAX_QUERIES = int(os.getenv("DB_MAX_QUERIES", "50000"))
DB_MAX_INACTIVE_LIFETIME = int(os.getenv("DB_MAX_INACTIVE_LIFETIME", "300"))
DB_COMMAND_TIMEOUT = int(os.getenv("DB_COMMAND_TIMEOUT", "30"))

DB_APPLICATION_NAME = os.getenv("DB_APPLICATION_NAME", "my_service")
DB_TCP_KEEPALIVES_IDLE = os.getenv("DB_TCP_KEEPALIVES_IDLE", "600")
DB_TCP_KEEPALIVES_INTERVAL = os.getenv("DB_TCP_KEEPALIVES_INTERVAL", "30")
DB_TCP_KEEPALIVES_COUNT = os.getenv("DB_TCP_KEEPALIVES_COUNT", "3")

# Configurações de retry em queries
DB_RETRY_BACKOFF_BASE = float(os.getenv("DB_RETRY_BACKOFF_BASE", "0.1"))  # segundos


# =============================================================================
# CONFIGURAÇÕES DE REDIS/CACHE
# =============================================================================

# Credenciais do Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# Configurações de cache
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 hora
CACHE_KEY_PREFIX = os.getenv("CACHE_KEY_PREFIX", "myapp:")

# URL de conexão Redis
REDIS_URL = os.getenv(
    "REDIS_URL",
    f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}" if REDIS_PASSWORD
    else f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
)

# =============================================================================
# CONFIGURAÇÕES DE SEGURANÇA
# =============================================================================

# Chaves secretas
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "encryption-key-32-chars-long")

# Configurações JWT
JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "3600"))  # 1 hora
JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", "604800"))  # 7 dias
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Configurações de segurança
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "True").lower() == "true"

# =============================================================================
# CONFIGURAÇÕES DE EMAIL
# =============================================================================

# Servidor SMTP
EMAIL_HOST = os.getenv("EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "False").lower() == "true"

# Credenciais de email
EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@myapp.com")
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "My Application")

# =============================================================================
# CONFIGURAÇÕES DE LOGGING
# =============================================================================

# Níveis de log
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Arquivos de log
LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))
LOG_FILE = os.getenv("LOG_FILE", "app.log")
LOG_MAX_SIZE = int(os.getenv("LOG_MAX_SIZE", "10485760"))  # 10MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))

# Configurações específicas
LOG_SQL_QUERIES = os.getenv("LOG_SQL_QUERIES", "True").lower() == "true"
LOG_REQUESTS = os.getenv("LOG_REQUESTS", "True").lower() == "true"

# =============================================================================
# CONFIGURAÇÕES DE UPLOAD/ARQUIVOS
# =============================================================================

# Diretórios
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
STATIC_DIR = Path(os.getenv("STATIC_DIR", "static"))
MEDIA_DIR = Path(os.getenv("MEDIA_DIR", "media"))

# Limitações de upload
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB
ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "jpg,jpeg,png,gif,pdf,doc,docx").split(",")

# =============================================================================
# CONFIGURAÇÕES DE APIS EXTERNAS
# =============================================================================

# AWS S3
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME", "")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# APIs de terceiros
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")

# =============================================================================
# CONFIGURAÇÕES DE MONITORAMENTO
# =============================================================================

# Sentry
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
SENTRY_ENVIRONMENT = os.getenv("SENTRY_ENVIRONMENT", "development")

# Métricas
METRICS_ENABLED = os.getenv("METRICS_ENABLED", "True").lower() == "true"
METRICS_PORT = int(os.getenv("METRICS_PORT", "8080"))

# =============================================================================
# CONFIGURAÇÕES DE CELERY (TASKS ASSÍNCRONAS)
# =============================================================================

# Broker
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

# Configurações de tasks
CELERY_TASK_SERIALIZER = os.getenv("CELERY_TASK_SERIALIZER", "json")
CELERY_RESULT_SERIALIZER = os.getenv("CELERY_RESULT_SERIALIZER", "json")
CELERY_TIMEZONE = os.getenv("CELERY_TIMEZONE", "UTC")

# =============================================================================
# CONFIGURAÇÕES ESPECÍFICAS DO AMBIENTE
# =============================================================================

# Configurações que variam entre development/production
TESTING = os.getenv("TESTING", "False").lower() == "true"
USE_HTTPS = os.getenv("USE_HTTPS", "False").lower() == "true"
MINIFY_HTML = os.getenv("MINIFY_HTML", "False").lower() == "true"
COMPRESS_RESPONSES = os.getenv("COMPRESS_RESPONSES", "False").lower() == "true"

# Timeouts
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
DB_QUERY_TIMEOUT = int(os.getenv("DB_QUERY_TIMEOUT", "30"))
CACHE_TIMEOUT = int(os.getenv("CACHE_TIMEOUT", "300"))

# =============================================================================
# VALIDAÇÕES E CONFIGURAÇÕES DERIVADAS
# =============================================================================

# Criar diretórios se não existirem
# for directory in [LOG_DIR, UPLOAD_DIR, STATIC_DIR, MEDIA_DIR]:
#     directory.mkdir(parents=True, exist_ok=True)

# Validações básicas
if not SECRET_KEY or SECRET_KEY == "dev-secret-key-change-in-production":
    if APP_ENVIRONMENT == "production":
        raise ValueError("SECRET_KEY deve ser definida em produção!")

if not DB_PASSWORD:
    raise ValueError("DB_PASSWORD é obrigatória!")

# URLs completas para uso na aplicação
BASE_URL = f"{'https' if USE_HTTPS else 'http'}://{SERVER_HOST}:{SERVER_PORT}"
API_URL = f"{BASE_URL}/api"
STATIC_URL = f"{BASE_URL}/static"
MEDIA_URL = f"{BASE_URL}/media"


# =============================================================================
# CONFIGURAÇÕES ESPECÍFICAS DA LLM
# =============================================================================
MODEL_NAME = "gemini-2.0-flash"