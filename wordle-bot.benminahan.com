server {
    client_max_body_size 64M;
    listen 80;
    server_name wordle-bot.benminahan.com;
    location / {
        proxy_pass             http://127.0.0.1:8000;
        proxy_read_timeout     60;
        proxy_connect_timeout  60;
        proxy_redirect         off;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}