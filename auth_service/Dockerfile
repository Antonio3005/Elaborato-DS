# Usa un'immagine di base con Python
FROM python:3.10-alpine

# Imposta il lavoro di lavoro nel container
WORKDIR /auth_service

RUN pip3 install --upgrade pip
COPY app.py ./
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

EXPOSE 5000

# Comando per avviare il servizio
CMD ["python", "app.py"]
