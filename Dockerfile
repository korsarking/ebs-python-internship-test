FROM python:3.11.4-slim

RUN apt-get update && apt-get install -y bash

WORKDIR /app/

COPY . /app/

RUN pip install poetry

RUN poetry config virtualenvs.create false && poetry install

RUN pip install -r requirements.txt

CMD ["bash", "/app/start.sh"]
