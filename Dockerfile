FROM node:19.4.0-bullseye-slim

COPY ./* /app/

WORKDIR /app

RUN npm install

CMD ["npm", "run"]

EXPOSE 8080
