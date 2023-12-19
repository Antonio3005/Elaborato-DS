# Usa un'immagine di base con Python
FROM python:3.11.5

# Imposta il lavoro di lavoro nel container
WORKDIR /auth_service

RUN pip3 install --upgrade pip
COPY app.py ./
#COPY ../db_users/users.sql /docker-entrypoint-initdb.d/
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
COPY templates ./templates

EXPOSE 5000

# Comando per avviare il servizio
CMD ["python", "app.py"]
