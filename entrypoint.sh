#!/bin/sh

# O shell irá parar o script se um comando falhar
set -e

# 1. Executa o script de migration do banco de dados.
echo "Running database migrations..."
python -m src.db.migrate

# 2. Executa o comando principal da aplicação (o que foi passado para o 'docker run' ou no CMD do Dockerfile).
# O "$@" pega todos os argumentos passados para o script e os executa.
# No nosso caso, será "uvicorn src.main:app --host 0.0.0.0 --port 8000".
exec "$@"