FROM python:3.12.4

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1



WORKDIR /home/python/app

# COPY requirements.txt .

# RUN pip install --no-cache-dir -r requirements.txt

# CORREÇÃO 1: Copia tudo do projeto para o contêiner.
COPY . .

# CORREÇÃO 2: Garante que o nosso script de entrada tenha permissão de execução.
# RUN chmod +x /home/python/app/entrypoint.sh

EXPOSE 8000

# CORREÇÃO 3: Define o nosso script como o ponto de entrada.
# ENTRYPOINT ["/home/python/app/entrypoint.sh"]
