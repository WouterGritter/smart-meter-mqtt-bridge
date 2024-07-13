FROM python:3.12-slim-bookworm

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY *.py ./
COPY smart_meter/*.py ./smart_meter/

ARG IMAGE_VERSION=Unknown
ENV IMAGE_VERSION=${IMAGE_VERSION}

CMD [ "python3", "-u", "main.py" ]
