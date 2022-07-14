FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim

RUN apt-get update && apt-get -y install cron sqlite3

# Copy cron file to the cron.d directory
COPY shift-cron /etc/cron.d/shift-cron
# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/shift-cron
# Apply cron job
RUN crontab /etc/cron.d/shift-cron


# Create directory for sqlite3 backups and log file
RUN mkdir ./borderlands_codes_bak && touch ./borderlands_codes_bak/log.err


# install python requirements
COPY ./requirements_docker.txt ./requirements_docker.txt
RUN pip3 install -r ./requirements_docker.txt

# Copy app
COPY ./app ./app

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--reload", "--port", "8080", "--host", "0.0.0.0"]