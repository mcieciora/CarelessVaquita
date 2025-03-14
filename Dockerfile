ARG PYTHON_BASE_IMAGE=python

FROM $PYTHON_BASE_IMAGE

WORKDIR /app

COPY requirements/example_app/requirements.txt /app

RUN pip3 install --no-cache-dir -r requirements.txt

ENTRYPOINT ["sleep", "180"]