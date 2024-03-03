FROM python:3.12-slim as build

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD [ "python","main.py"]
