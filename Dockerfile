FROM ubuntu:22.04
RUN apt update -y
RUN apt install python3-venv -y
WORKDIR /home/wordle-bot
RUN python3 -m venv .venv
COPY requirements.txt requirements.txt
RUN . .venv/bin/activate && pip install -r requirements.txt
COPY gunicorn_conf.py gunicorn_conf.py 
RUN apt install nginx -y
COPY wordle-bot.benminahan.com /etc/nginx/sites-available/wordle-bot.benminahan.com
RUN ln -s /etc/nginx/sites-available/wordle-bot.benminahan.com /etc/nginx/sites-enabled/
RUN apt install certbot python3-certbot-nginx -y
COPY . .
ENTRYPOINT ["./entrypoint.sh"]