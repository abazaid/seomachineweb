FROM node:20-alpine

WORKDIR /app/frontend

COPY frontend/package.json /app/frontend/package.json
RUN npm install

COPY frontend /app/frontend

ENV NEXT_PUBLIC_API_BASE=http://localhost:8000/api/v1

CMD ["npm", "run", "dev"]
