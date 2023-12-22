FROM python:3.11.5

# Imposta il lavoro di lavoro nel container
WORKDIR /subscription_service

RUN pip3 install --upgrade pip
COPY subscription.py ./
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
COPY templates ./templates


EXPOSE 5001

# Comando per avviare il servizio
CMD ["python", "subscription.py"]