# Usa un'immagine di base con Python
FROM python:3.10

# Imposta il lavoro di lavoro nel container
WORKDIR /app

# Copia i file necessari nel container
COPY requirements.txt .
COPY app.py .

# Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Esponi la porta su cui il servizio ascolta
EXPOSE 5000

# Comando per avviare il servizio
CMD ["python", "app.py"]
