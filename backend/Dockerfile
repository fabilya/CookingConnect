FROM python:3.7-slim
WORKDIR /app
COPY . .
RUN pip3 install --upgrade pip && pip3 install -r ./requirements.txt --no-cache-dir
CMD ["gunicorn", "cookingconnect.wsgi:application", "--bind", "0.0.0.0:8000"]
