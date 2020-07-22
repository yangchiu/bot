FROM python:3.8.5-alpine3.12

COPY requirements.txt /srv
WORKDIR /srv
RUN pip install -r requirements.txt

COPY . /srv

CMD ["gunicorn", "longhorn_github_bot:app"]
