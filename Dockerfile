FROM python:3.9-slim

RUN apt-get update && apt-get -y install cron sqlite3

# Copy cron file to the cron.d directory
COPY shift-cron /etc/cron.d/shift-cron
# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/shift-cron
# Apply cron job
RUN crontab /etc/cron.d/shift-cron


# Create directory for sqlite3 backups and log file
RUN mkdir ./borderlands_codes_bak && touch ./borderlands_codes_bak/log.err


# Installation required for selenium
RUN apt-get update -y \
    && apt-get install --no-install-recommends --no-install-suggests -y tzdata ca-certificates wget bzip2 libxtst6 libgtk-3-0 libx11-xcb-dev libdbus-glib-1-2 libxt6 libpci-dev \
    && apt-get install --no-install-recommends --no-install-suggests -y `apt-cache depends firefox-esr | awk '/Depends:/{print$2}'` \
    && update-ca-certificates \
    # Cleanup unnecessary stuff
    && apt-get purge -y --auto-remove \
                  -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/* /tmp/*

# install firefox
RUN FIREFOX_SETUP=firefox-setup.tar.bz2 && \
    wget -O $FIREFOX_SETUP "https://download.mozilla.org/?product=firefox-88.0&os=linux64" && \
    tar xjf $FIREFOX_SETUP -C /opt/ && \
    ln -s /opt/firefox/firefox /usr/bin/firefox && \
    rm $FIREFOX_SETUP


# install python requirements
COPY ./requirements_docker.txt /app/requirements_docker.txt
RUN pip3 install -r /app/requirements_docker.txt

ARG USER=admin
ARG UID=1000
ARG GID=1000
ARG GROUP=admin

RUN mkdir /db
RUN chown -R $UID:$GID /db
RUN chmod 777 /db

# Copy app
WORKDIR /app
COPY ./app ./app

RUN chown -R $UID:$GID /app \
  && groupadd -g $GID $GROUP \
  && useradd -m -u $UID -g $GID -o -s /bin/bash $USER

USER $USER

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]