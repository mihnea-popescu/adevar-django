# Use Python 3.10 slim image (faster builds)
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies for PostgreSQL, Pillow, etc.
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && apt-get clean

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/

EXPOSE 8000

CMD ["gunicorn", "mysite.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
