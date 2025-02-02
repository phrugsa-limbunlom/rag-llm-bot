FROM node:14

WORKDIR /picksmart-app

COPY package.json ./
COPY package-lock.json ./

RUN npm install

COPY . .

CMD ["npm", "start"]

EXPOSE 3000