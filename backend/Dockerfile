FROM python:3.11-slim
RUN apt-get update &&\
    apt-get upgrade -y &&\
    apt-get install -y libpq-dev gcc netcat-traditional
WORKDIR /app
COPY requirements.txt ./
RUN pip install -U pip &&\
    pip install -r requirements.txt --no-cache-dir
COPY . .
RUN chmod +x run_app.sh
CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000