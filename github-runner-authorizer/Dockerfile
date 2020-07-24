FROM python:3.8.5-alpine3.12

RUN apk add --virtual build gcc libffi-dev musl-dev openssl-dev
COPY requirements.txt /srv
WORKDIR /srv
RUN pip install -r requirements.txt
RUN apk del build

COPY . /srv

CMD ["python", "-m", "github_runner_authorizer"]
