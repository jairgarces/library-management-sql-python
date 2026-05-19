Current Status (Development Build)
This project is in active development. The following components are fully implemented and functional:
Implemented
Application startup (main.py)
Database connection (db.py)
Student Module:
• Create Student
• Create Cart
• Add Book to Cart
• Place Order
• Update Cart (modify/delete items)
• Cancel Order
• Add Book Review
Reports Module Framework:
• “Run Report by Number” works
• Report #1 and #2 implemented
Tkinter GUI windows fully functional
Reusable Cart Logic:
After checkout, the student’s cart is emptied and automatically reset to Active so they may continue shopping.


Not Implemented Yet
Admin Module (books, inventory, universities, courses)
Customer Service Module (tickets)
Super Admin Module (employee management)
Full report set (#3–#20)
Loading the full real sample dataset (currently using demo data)


How to Run the Application
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

Note: This uses a lightweight demo dataset for development.
The final project will use the complete sample dataset later.

Run the App
python src/main.py
Available Features (How to Test)
Student Module
Open from main menu → Student Module


You can test:
Create Student
Create Cart (enter existing student_id)
Add Book to Cart (cart_id, book_id, quantity)
Update Cart (change/remove items; inventory adjusts)
Place Order (cart_id + payment/shipping info)
Cancel Order (restores inventory)
Add Review (student_id, book_id, rating)
Reports Module
Open from main menu → Reports
Enter 1 → Run Report (students from St Thomas University)
Enter 2 → Run Report (graduate students; demo data may return 0 rows)
More reports will be added as development continues.


Notes for Group Members
This is a development build, not the final product.
Once all modules are implemented, we will:
Load the real sample dataset
Add all 20 required reports
Record the demo video
Finalize documentation and deliverables


Cart Reuse Behavior
Each student has exactly one reusable cart.
After a successful checkout, the cart’s items are converted into an order, then the cart is automatically emptied and reactivated so the student can make new purchases without creating a new cart.