# Telegram Bot for Better Contract Understanding

## Project Overview

This project is a Telegram Bot written in Python that interacts with a MariaDB database to provide users with term definitions related to legal contracts and documents. Users can:
Upload contracts or documents for analysis, where the bot identifies relevant terms and returns their definitions from the database.
Directly access dictionaries without uploading files, retrieving terms and their definitions from either Italian or English dictionaries.
View a list of labor unions offices and patronati del lavoro in the city of Verona for additional support or consultation.
Switch languages between Italian and English for bot interaction and definitions.
Receive useful links to articles and websites related to the user’s query, offering further reading and assistance.

The entire project is containerized using Docker, ensuring easy deployment and scalability. The bot interacts with both the Telegram API and a MariaDB database to provide real-time contract term extraction and definition matching.


---

## Features

- **User Uploads**: Users can upload contract documents directly through the Telegram bot.
- **Text Extraction**: The bot reads and processes the text from the uploaded file.
- **Term Matching**: Extracted words from the contract are matched against pre-defined lists of terms stored in two separate MariaDB tables (`dizionario_it` and `dizionario_en`).
  - **`dizionario_ita`**: Contains Italian terms and their definitions in Italian.
  - **`dizionario_eng`**: Contains Italian terms and their definitions in English.
- **Dictionary Access**: Users can query the dictionary directly, without uploading any files.
- **Useful Links**: The bot can provide links to articles or websites relevant to the user's inquiries.
- **Labor Unions and Patronati Offices**: The bot can display a list of **sindacati** (labor unions) and **patronati** (social support offices) located in the city of Verona.
- **Language Switching**: Users can switch between Italian and English language modes.
- **Fully Containerized**: The bot and its components (Telegram bot, database, etc.) run inside Docker containers for easy deployment and management.
- **Scalability**: Thanks to Docker, the system is designed to scale across multiple environments, including cloud services and Raspberry Pi.

---


## Project Structure

```
├── .github/workflows/
│   └── docker-publish.yml    # Workflow for automated Docker publishing
├── .gitignore                # Files to ignore during version control
├── LICENSE                   # Project License
├── README.md                 # Project documentation
├── app.py                    # Main bot logic and Telegram interaction
├── dockerfile                # Dockerfile for building the bot image
├── example.env               # Example environment file for configuration
├── requirements.txt          # Python dependencies
├── sql.py                    # Utility functions for database interaction
```

### Main Components

- **`app.py`**: Contains the core logic for the Telegram bot, including file handling, text processing, dictionary queries, language switching, and useful links functionality.
- **`dockerfile`**: Defines the Docker image for the bot, including the Python environment and the required dependencies.
- **`sql.py`**: Manages database connections and queries, ensuring smooth interaction with the MariaDB instance.
- **`requirements.txt`**: Lists all necessary Python libraries, including `pymysql`, `spacy`, and others.

## Prerequisites

- **Docker**: Make sure Docker is installed on your system.
- **MariaDB**: The bot relies on a MariaDB instance to store and retrieve legal terms and definitions. You can use Docker to run the MariaDB container as well.

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/wrathgewp/Project_Work.git
```

### 2. Environment Setup

Before running the bot, create an `.env` file in the root of the project based on the `example.env` file. This file should contain the necessary environment variables such as your Telegram bot token and database credentials.

Update `.env` with your specific details.

### 3. Docker Setup

Build and run the Docker containers for both the bot and the MariaDB database.

#### Build the Docker Image

```bash
docker build -t telegram-bot .
```

#### Running the Containers

You can use Docker Compose to spin up both the bot and the database:

```bash
docker-compose up
```


### 4. Add Data to the Database

You can manually populate the MariaDB database using a SQL script or through a database manager like `phpMyAdmin`.

Example SQL query to insert data:

```sql
INSERT INTO dizionario_it (parola, descrizione) VALUES ('Retribuzione Minima', 'The minimum salary as per contract.');
INSERT INTO dizionario_en (parola, descrizione) VALUES ('Retribuzione Minima', 'The minimum salary according to the contract.');
```

### 5. Testing the Bot

Once the bot is running, you can interact with it through Telegram by sending `/upload` followed by uploading a file, or by directly accessing the dictionary with a command.

## Usage

### Functions

W.I.P. /comuni  /syndicates

### Supported Languages

- **Italian** (default)
- **English**

The bot can provide dictionary definitions in both Italian and English, based on user preference.

## Dependencies

- **Python 3.x**
- **Docker**
- **MariaDB**
- **Python Libraries**: 

```python
from sql import connection
import os
from dotenv import load_dotenv
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, Updater, CallbackQueryHandler
import pymysql
from pymysql.err import MySQLError
import sql
from sql import get_dizionario
```

Install dependencies locally with:

```bash
pip install -r requirements.txt
```

## Contributing

Feel free to submit issues or pull requests if you would like to contribute to the project. Please follow the standard GitHub workflow for collaboration.

1. Fork the project
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

## License

W.I.P.

## Future Enhancements

- Implement support for additional document formats (e.g., PDF, DOCX).
- Add more sophisticated natural language processing (NLP) for term extraction (from spaCy to DistilBERT).
- Improve matching algorithm for more accurate term extraction.
- Integrate additional dictionaries or databases to broaden the range of terms and definitions available.
