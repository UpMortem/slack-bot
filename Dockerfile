FROM python:3.11.3-slim
ENV PYTHONUNBUFFERED True

# TO FETCH https://github.com/UpMortem/pinecone-python-client FOR TESTING
RUN apt update &&\
    apt install -y git

WORKDIR /app

COPY requirements.txt .
COPY src/semantic_search/requirements.txt semantic_search_requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -r semantic_search_requirements.txt

COPY ./src ./src

CMD exec uvicorn index:app --host 0.0.0.0 --port $PORT --workers 2 --timeout-keep-alive 600 --app-dir /app/src

EXPOSE 8080
