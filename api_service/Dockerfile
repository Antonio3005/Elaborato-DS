FROM python:3.11.5
# Imposto il lavoro di lavoro nel container
WORKDIR /api_service

COPY . .
#COPY api.py ./
#COPY requirements.txt ./
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip install Flask --upgrade

#CMD ["python", "api.py"]
CMD ["flask","--app", "api", "run", "--host=0.0.0.0"]
