FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim

COPY ./app ./app
COPY ./requirements_docker.txt ./requirements_docker.txt
COPY ./borderlands_codes.db ./borderlands_codes.db

RUN pip3 install -r ./requirements_docker.txt
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--reload", "--port", "8080", "--host", "0.0.0.0"]