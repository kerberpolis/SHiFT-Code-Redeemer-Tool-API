FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

WORKDIR /app

COPY ./requirements.txt /app/requirements_docker.txt
RUN pip3 install -r requirements_docker.txt

COPY ./app /app/app
COPY ./tests /app/tests

COPY .flake8 /app/.flake8
