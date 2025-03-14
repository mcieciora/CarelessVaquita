ARG PYTHON_BASE_IMAGE=python

FROM $PYTHON_BASE_IMAGE

WORKDIR /app

COPY requirements/merge_bot/requirements.txt /app
COPY tools/python/merge_bot.py .
COPY required_reviewers .

RUN pip3 install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "merge_bot.py"]