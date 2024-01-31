FROM python:3.11.5
WORKDIR /notifier_service

COPY . .
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip install Flask --upgrade

CMD ["python", "notifier.py"]

