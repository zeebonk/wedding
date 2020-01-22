FROM python:3.8.1-slim-buster
WORKDIR /app

RUN pip install pipenv==2018.11.26
ENV PIPENV_COLORBLIND 1
ENV PIPENV_HIDE_EMOJIS 1
ENV PIPENV_NOSPIN 1

COPY Pipfile Pipfile.lock ./
RUN pipenv install --deploy

COPY wedding ./wedding/

ENTRYPOINT pipenv run python -m wedding
