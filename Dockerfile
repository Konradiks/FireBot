FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY manage.py manage.py
COPY dashboard/ dashboard/
COPY FireBot/ FireBot/
COPY static/ static/
COPY templates/ templates/
COPY worker/ worker/

COPY entrypoint.sh entrypoint.sh
RUN chmod +x entrypoint.sh

# CMD ["./entrypoint.sh"]
