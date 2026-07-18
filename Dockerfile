FROM python:3.13-slim

WORKDIR /code

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && gunicorn Food.wsgi:application --bind 0.0.0.0:8000"]