FROM mhart/alpine-node:10

WORKDIR /app
COPY . .

RUN npm i
RUN npm run build

EXPOSE 8080
CMD ["npm", "run", "start"]
