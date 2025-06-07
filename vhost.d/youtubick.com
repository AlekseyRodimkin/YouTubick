location /static/ {
    alias /app/static/;
    access_log off;
    expires 1d;
}

location = /favicon.ico {
    alias /app/static/favicon.ico;
    access_log off;
    expires 1d;
}