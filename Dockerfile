FROM node:19.4.0-bullseye-slim

COPY ./* /app/

WORKDIR /app

RUN npm install
RUN npm run build

CMD ["npm", "start"]

EXPOSE 8080
