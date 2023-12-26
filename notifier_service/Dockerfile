FROM python:3.11.5

# Imposta il lavoro di lavoro nel container
WORKDIR /notifier_service

RUN pip3 install --upgrade pip
COPY notifier.py ./
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 5003

# Comando per avviare il servizio
CMD ["python", "notifier.py"]
