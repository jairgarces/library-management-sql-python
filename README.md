# Library Management SQL Python

## Overview

This repository contains Python code for a library management system that connects to a local MySQL database. The application provides a Python GUI that allows users to add, delete, and retrieve data via forms and reports from the database, simulating a basic school library management application.

---

## Installation Instructions

### Requirements

Before running the application, ensure you have the following installed:

- Python 3.11
- MySQL 8.x
- `mysql-connector-python`

### Install Python Dependencies

Install the MySQL connector package:

```bash
pip install mysql-connector-python
```

---

## Database Setup

1. Open MySQL Workbench and create a local database connection.

2. Using the provided SQL files, create the database schema and demo data.

Run the following SQL scripts in this order:

```bash
mysql -u <user> -p <database> < sql/drop_tables.sql
mysql -u <user> -p <database> < sql/create_tables.sql
mysql -u <user> -p <database> < sql/insert_demo_data.sql
```

3. Open the `db.py` file and update the `DB_CONFIG` object with your local MySQL credentials.

Example:

```python
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "Antonio",
    "password": "",
    "database": "book_fetch",
}
```

---

## Usage Instructions

### Running the Application

Run the following command from the project root directory:

```bash
python src/main.py
```

### Using the Application

1. Launch the application.
2. Select a module from the main menu.
3. Enter data into the provided forms.
4. Click the submit button to insert or update records in the database.

You can monitor live database changes using MySQL Workbench in split-screen view while interacting with the application.

The Reports section allows users to generate reports based on database data. Some reports are partially implemented and may not yet provide complete functionality.

---

## Features

- Add records to the database
- Delete records from the database
- Retrieve and display data
- GUI-based form interaction using Python
- MySQL database integration
- Basic reporting functionality

---

## Technologies Used

- Python
- MySQL
- MySQL Workbench
- mysql-connector-python

## Authors

 - Jair Garces
 - Kevin Rivera
 - Steven Schmitz
 - Nate Agbemadon
 - Collin Ryan
