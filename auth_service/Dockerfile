FROM python:3.11.5
# Imposta il lavoro di lavoro nel container
WORKDIR /auth_service

COPY . .
#COPY auth.py ./
#COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip install Flask --upgrade
#COPY templates ./templates
#ENV SECRET_KEY="chiavesegreta"

# Comando per avviare il servizio
#CMD ["python", "auth.py"]
CMD ["flask","--app", "auth", "run", "--host=0.0.0.0"]
