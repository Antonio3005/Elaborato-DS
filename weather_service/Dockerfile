# Usa un'immagine di base con Python
FROM python:3.11.5


# Imposta il lavoro di lavoro nel container
WORKDIR /weather_service

RUN pip3 install --upgrade pip
COPY choice_temp.py ./
COPY requirements.txt ./
COPY templates /templates
RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 5001

# Comando per avviare il servizio
CMD ["python", "choice_temp.py"]