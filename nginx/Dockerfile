# Stage 1 — Build the React frontend
FROM node:18-alpine AS react_build

WORKDIR /frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ .

# This env var tells Axios to call /api on the same domain.
# Nginx will proxy /api → backend container.
ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# Stage 2 — Serve with Nginx
FROM nginx:1.25-alpine

# Copy React build output
COPY --from=react_build /frontend/dist /usr/share/nginx/html

# Copy nginx config (HTTP — used before SSL is set up)
COPY nginx/conf.d/vihub.conf /etc/nginx/conf.d/default.conf

# Certbot challenge directory
RUN mkdir -p /var/www/certbot

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
