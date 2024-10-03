# Use the latest Python base image
FROM python:latest

# Set the UID and GID environment variables to 1000.
ENV UID=1000 GID=1000

LABEL Maintainer="I quasi creativi"

# Set the working directory
WORKDIR /app/telegram_bot

# Copy the requirements file into the container
COPY ./* /app/telegram_bot/

# Create standard user and group
RUN groupadd -g ${GID} quasicreativi && \
    useradd -m -d /app -s /bin/bash -g quasicreativi -u ${UID} quasicreativi

# Create the app directory and set ownership to the quasicreativi user
RUN mkdir -p /app/.local && chown -R quasicreativi:quasicreativi /app

# Switch to the quasicreativi user
USER quasicreativi

# Set the working directory
RUN mkdir -p /app/downloads

#Install the required packages
RUN pip install --no-cache-dir -r /app/telegram_bot/requirements.txt

#Execute the app
CMD [ "python", "-u", "app.py"]