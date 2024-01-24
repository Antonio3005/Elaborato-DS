FROM python:3.11.5
# Imposta il lavoro di lavoro nel container
WORKDIR /sla_manager

COPY . .
#COPY auth.py ./
#COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip install Flask --upgrade

CMD ["flask","--app","sla", "run", "--host=0.0.0.0", "--port=5005"]