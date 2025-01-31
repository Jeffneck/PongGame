FROM nginx:latest

# Copie de la config Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copie du script d'entrée
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 80 443

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
