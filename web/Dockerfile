FROM node:24-alpine
WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
ARG NEXUS_API_URL=http://api:8000
RUN npm run build
USER node
CMD ["npm", "start"]
