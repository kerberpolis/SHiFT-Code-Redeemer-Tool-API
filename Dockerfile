FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim

COPY ./requirements_docker.txt ./requirements_docker.txt
RUN pip3 install -r ./requirements_docker.txt

COPY ./app ./app

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--reload", "--port", "8080", "--host", "0.0.0.0"]