# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster


WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt


COPY src /app/src

WORKDIR /app/src


CMD [ "python3","-u" ,"-m" ,"uvicorn", "main:app" , "--reload", "--host=0.0.0.0"]

