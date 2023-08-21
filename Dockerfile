FROM python:3.11.3-slim
ENV PYTHONUNBUFFERED True

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src

# Cache the tiktoken encoding file
RUN python -c "import tiktoken; tiktoken.encoding_for_model('gpt-3.5-turbo-0613')"

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 index:flask_app --chdir /app/src

EXPOSE 8080
