FROM python:3.11.5
# Imposta il lavoro di lavoro nel container
WORKDIR /subscription_service

COPY . .
#COPY subscription.py ./
#COPY requirements.txt ./
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip install Flask --upgrade
#COPY templates ./templates

# Comando per avviare il servizio
#CMD ["python", "subscription.py"]
CMD ["flask","--app", "subscription", "run", "--host=0.0.0.0"]