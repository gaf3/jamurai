FROM python:3.13-alpine3.20

RUN mkdir -p /opt/service

WORKDIR /opt/service

ADD requirements.txt .

RUN pip install -r requirements.txt

COPY setup.py .
COPY lib lib

ENV PYTHONPATH "/opt/service/lib:${PYTHONPATH}"
