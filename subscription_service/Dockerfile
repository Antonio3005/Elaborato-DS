FROM python:3.11.5
WORKDIR /subscription_service

COPY . .
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip install Flask --upgrade
CMD ["flask","--app", "subscription", "run", "--host=0.0.0.0"]