FROM python:3.13-slim

WORKDIR /app

# System deps needed by Django / cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirenments.txt .

RUN pip install --no-cache-dir \
    asgiref==3.11.1 \
    Django==6.0.3 \
    django-cors-headers==4.9.0 \
    djangorestframework==3.17.1 \
    djangorestframework_simplejwt==5.5.1 \
    PyJWT==2.12.1 \
    python-dotenv==1.2.2 \
    sqlparse==0.5.5 \
    gunicorn

COPY . .

# Data directory for SQLite (mounted as a volume at runtime)
RUN mkdir -p /data

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 2"]
