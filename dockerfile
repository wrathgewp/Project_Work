#Deriving the latest base image of python

FROM python:latest

ENV UID=1000 GID=1000

LABEL Maintainer="I quasi creativi"

WORKDIR /app/telegram_bot

# This will copy the remote file at working directory in container

COPY ./* /app/telegram_bot

RUN groupadd -g ${GID} quasicreativi && \
useradd -m -d /app -s /bin/bash -g quasicreativi -u ${UID} quasicreativi

RUN chown -R quasicreativi /app/telegram_bot

# Create the directory for downloaded files

RUN mkdir -p /app/downloads

RUN chown -R quasicreativi /app/downloads

# Change the user

USER quasicreativi

## This will install all the dependencies

RUN pip install --no-cache-dir -r /app/telegram_bot/requirements.txt

## This will execute the code

CMD [ "python", "-u", "app.py"]