FROM nginx:1.24-bullseye

RUN rm /etc/nginx/conf.d/default.conf
COPY routing.conf /etc/nginx/conf.d/routing.conf
RUN apt update &&  \
    apt autoclean && apt -f install && apt-get install -y nginx-extras vim