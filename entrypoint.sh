#!/bin/bash -e

nginx
certbot -n --nginx -d wordle-bot.benminahan.com --agree-tos -m ${CERTBOT_EMAIL}
/home/wordle-bot/.venv/bin/gunicorn -c gunicorn_conf.py main:app &
tail -f /var/log/nginx/*.log /home/wordle-bot/*_log