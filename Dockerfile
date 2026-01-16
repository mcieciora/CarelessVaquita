# CHANGE

ARG DEFAULT_IMAGE_TAG=3.14.2-alpine

FROM python:${DEFAULT_IMAGE_TAG}

WORKDIR /app

COPY requirements/example_app/requirements.txt /app

RUN pip3 install --no-cache-dir -r requirements.txt

ENTRYPOINT ["sleep", "180"]