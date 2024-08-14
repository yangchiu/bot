FROM python:3.10.14-alpine

COPY requirements.txt /srv
WORKDIR /srv
RUN pip install -r requirements.txt

COPY . /srv

CMD ["gunicorn", "longhorn_github_bot:app"]
