# library-management-sql-python overview
This repo holds Python code for a Library management system that connects to a local SQL database. You can add,delete,and get specific data through the Python GUI which acts like an application for a school library. 


# Database setup
Use SQL workbench and create a database connection. Using the provided sql files, create a schema. 
In the file 'db.py' go to DB_CONFIG and enter your sql information to connect to your created database. 

EXAMPLE:
    DB_CONFIG = {
        "host": "localhost",
        "port": 3306,  #your port
        "user": "Antonio", #your sql username
        "password": "", # yoursqlpassword
        "database": "book_fetch",  # or whatever schema name you used
    }


# How to Run the Application
Requirements:
Python 3.11
MySQL 8.x
mysql-connector-python package
Install connector:
pip install mysql-connector-python
Database Setup (Temporary Demo Data)
Run these SQL scripts in this order:
mysql -u <user> -p <database> < sql/drop_tables.sql
mysql -u <user> -p <database> < sql/create_tables.sql
mysql -u <user> -p <database> < sql/insert_demo_data.sql


Run the App
python src/main.py

# How to use the application
From the menu, select a module and begin entering data for the given forms, once you've entered the required fields, click submit. You can see live updates in your SQL workbench if you have it open in splitscreen view. Clicking the reports section will allow you to see reports of the data in your database, note that not all of these reports have been fully implemented. 
