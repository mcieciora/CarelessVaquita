ARG PYTHON_BASE_IMAGE=python

FROM $PYTHON_BASE_IMAGE

WORKDIR /app
COPY requirements /app/requirements
COPY pytest.ini ./

WORKDIR /app/automated_tests
COPY automated_tests .

WORKDIR /app/src
COPY src .

WORKDIR /app/tools/python
COPY tools/python .

WORKDIR /app
RUN python -m pip install --no-cache-dir -r requirements/example_app/requirements.txt -r requirements/testing/requirements.txt -r requirements/merge_bot/requirements.txt