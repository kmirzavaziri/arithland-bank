FROM python:3.11-alpine

WORKDIR /app

RUN apk add --no-cache gcc musl-dev postgresql-dev python3-dev

COPY requirements/python/ ./requirements/python/

RUN pip install --no-cache-dir -r requirements/python/production.txt

COPY . .

RUN mkdir -p /app/staticfiles

EXPOSE 8000

CMD sh -c "python manage.py migrate && \
    python manage.py collectstatic --noinput && \
    gunicorn bank.wsgi:application --bind 0.0.0.0:8000 --workers 4"
