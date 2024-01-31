FROM python:3.11.5
WORKDIR /sla_manager

COPY . .
RUN pip install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip install Flask --upgrade

CMD ["flask","--app","sla", "run", "--host=0.0.0.0"]