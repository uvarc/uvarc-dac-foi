FROM nginx:1.21-alpine

COPY templates/ /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]