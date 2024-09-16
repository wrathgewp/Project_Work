#Deriving the latest base image of python

FROM python:latest

LABEL Maintainer="I quasi creativi"

WORKDIR /usr/app/telegram_bot

# This will copy the remote file at working directory in container

COPY ./* ./

## This will install all the dependencies

RUN pip install --no-cache-dir -r requirements.txt

## This will execute the code

CMD [ "python", "-u", "app.py"]