FROM python:3.11.4-slim

RUN apt-get update && apt-get install -y bash

RUN pip install poetry

WORKDIR /app/

COPY . /app/

RUN poetry install

CMD ["bash", "/app/start.sh"]
