FROM node:20-bookworm-slim AS frontend

WORKDIR /app/hackharvard_frontend
COPY hackharvard_frontend/package*.json ./
RUN npm ci
COPY hackharvard_frontend ./
RUN npm run build

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY stablediffusion_dixit ./stablediffusion_dixit
COPY premade_animations ./premade_animations
COPY --from=frontend /app/hackharvard_frontend/dist ./hackharvard_frontend/dist

CMD ["python", "-m", "stablediffusion_dixit.backend.endpoints"]
