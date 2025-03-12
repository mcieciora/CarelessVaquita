FROM python:3.13.2-alpine

WORKDIR /app

COPY requirements/merge_bot/requirements.txt /app
COPY tools/python/merge_bot.py .
COPY required_reviewers .

RUN pip3 install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "merge_bot.py"]