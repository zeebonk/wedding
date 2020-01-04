FROM python:3.8.0-buster
WORKDIR /app

RUN pip install pipenv==2018.11.26

COPY Pipfile Pipfile.lock ./
RUN pipenv install --deploy

COPY . /app

ENTRYPOINT pipenv run python main.py
