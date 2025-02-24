FROM nginx:1.21-alpine

COPY html/ /usr/share/nginx/html
COPY html/static/ /usr/share/nginx/html/static

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]