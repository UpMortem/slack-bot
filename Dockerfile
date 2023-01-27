FROM python:3.10-slim
ENV PYTHONUNBUFFERED True

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 index:flask_app --chdir /app/src

EXPOSE 8080
