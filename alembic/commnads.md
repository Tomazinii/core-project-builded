# Ver histórico de migrations
alembic history

# Ver SQL que será executado (sem aplicar)
alembic upgrade head --sql

# Reverter a última migration
alembic downgrade -1

# Reverter tudo
alembic downgrade base

# Verificar status atual
alembic current

# Ver migrations pendentes
alembic history --verbose