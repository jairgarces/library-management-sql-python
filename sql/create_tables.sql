-- =====================================================================
--  BookFetch - Phase 4 Physical Design
--  create_tables.sql
--
--  ORIGINAL RELATIONAL SCHEMA (FROM PHASE 3 PDF - WITH ORIGINAL NAMES)
--
--  Student(student_id PK, university_id FK, address_id FK,
--          first_name, last_name, email UNIQUE, phone UNIQUE,
--          birth_date, major, student_status, year, username UNIQUE)
--
--  Employee(employee_id PK, address_id FK,
--           first_name, last_name, gender, salary, ssn UNIQUE,
--           email UNIQUE, phone UNIQUE, role)
--
--  Account_audit(audit_id PK,
--                target_employee FK, performed_by FK,
--                action_type, action_time, note)
--
--  Address(address_id PK, street, city, state, zip)
--
--  University(university_id PK, address_id FK,
--             name, rep_first_name, rep_last_name,
--             rep_email, rep_phone)
--
--  Department(department_id PK, university_id FK, name)
--
--  Instructor(instructor_id PK,
--             university_id FK, department_id FK,
--             first_name, last_name, email)
--
--  Course(course_id PK, department_id FK, name, code)
--
--  Course_Instructor(PK(course_id, instructor_id, year, semester))
--
--  Category(category_id PK, name)
--  Subcategory(subcategory_id PK, name)
--  Keyword(keyword_id PK, term)
--  Author(author_id PK, name)
--
--  Book(book_id PK, category_id FK,
--       title, publisher, published_date, edition, language,
--       isbn13 UNIQUE, isbn10 UNIQUE,
--       condition, acquisition_type, price, quantity >= 0, weight, format)
--
--  BookAuthor(PK(book_id, author_id))
--  BookSubcategory(PK(book_id, subcategory_id))
--  BookKeyword(PK(book_id, keyword_id))
--
--  Review(review_id PK, student_id FK, book_id FK, rating BETWEEN 1 AND 5)
--
--  Course_Book(PK(course_id, book_id))
--
--  Ticket_category(ticket_category_id PK, name)
--
--  Ticket(ticket_id PK,
--         category_id FK,
--         created_by_student FK,
--         created_by_cs FK,
--         resolved_by_admin FK,
--         created_at, title, status, ...)
--
--  Ticket_state_history(history_id PK, ticket_id FK, employee_id FK)
--
--  Cart(cart_id PK, student_id UNIQUE FK)
--  Cart_item(PK(cart_id, book_id), quantity > 0)
--
--  Order(order_id PK, student_id FK, ...)
--  Orderitem(PK(order_id, book_id), ...)
--  PurchaseHistory(PK(student_id, book_id, order_id, purchase_date))
--
--  PHYSICAL IMPLEMENTATION CHOICES (THIS FILE)
--  - Consistent snake_case naming for all tables and columns.
--  - "Order" table renamed to customer_order, and Orderitem to order_item
--    to avoid reserved words and follow snake_case.
--  - Book column "condition" renamed to book_condition for clarity.
--  - Employee roles stored in employee.role using	
--    ENUM('customer_support','admin','super_admin').

-- Note: address and university are created first so that foreign key
-- constraints from student can be defined. In the Phase 3 report they
-- are listed later, but SQL requires this dependency order.

-- Role-based access control is supported by storing an employee’s role in the employee.role column (customer_support, admin, super_admin). 
-- Actual enforcement of which screens and actions are available to each role will be implemented in the application 
-- layer (Phase 5), not by additional database constraints.
-- =====================================================================

CREATE DATABASE IF NOT EXISTS book_fetch;
USE book_fetch;

-- ======================
--  Address & University
-- ======================

CREATE TABLE address (
    address_id  INT AUTO_INCREMENT PRIMARY KEY,
    street      VARCHAR(100) NOT NULL,
    city        VARCHAR(100) NOT NULL,
    state       VARCHAR(50)  NOT NULL,
    zip         VARCHAR(20)  NOT NULL
);

CREATE TABLE university (
    university_id   INT AUTO_INCREMENT PRIMARY KEY,
    address_id      INT NOT NULL,
    university_name VARCHAR(150) NOT NULL,
    rep_first_name  VARCHAR(50),
    rep_last_name   VARCHAR(50),
    rep_email       VARCHAR(100),
    rep_phone       VARCHAR(20),
    FOREIGN KEY (address_id) REFERENCES address(address_id)
		ON DELETE RESTRICT
);

CREATE TABLE department (
    department_id   INT AUTO_INCREMENT PRIMARY KEY,
    university_id   INT NOT NULL,
    department_name VARCHAR(100) NOT NULL,
    FOREIGN KEY (university_id) REFERENCES university(university_id)
		ON DELETE CASCADE
);

CREATE TABLE instructor (
    instructor_id   INT AUTO_INCREMENT PRIMARY KEY,
    university_id   INT NOT NULL,
    department_id   INT NOT NULL,
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    email           VARCHAR(100) NOT NULL UNIQUE,
    FOREIGN KEY (university_id) REFERENCES university(university_id)
		ON DELETE RESTRICT,
    FOREIGN KEY (department_id) REFERENCES department(department_id)
		ON DELETE RESTRICT
);

-- =========
-- Students
-- =========

CREATE TABLE student (
    student_id      INT AUTO_INCREMENT PRIMARY KEY,
    university_id   INT NOT NULL,
    address_id      INT NOT NULL,
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    email           VARCHAR(100) NOT NULL UNIQUE,
    phone           VARCHAR(20),
    birth_date      DATE,
    major           VARCHAR(100),
    student_status  VARCHAR(50),
    Student_year    VARCHAR(20),
    username        VARCHAR(50) NOT NULL UNIQUE,
    FOREIGN KEY (university_id) REFERENCES university(university_id)
		ON DELETE RESTRICT,
    FOREIGN KEY (address_id) REFERENCES address(address_id)
		ON DELETE RESTRICT
);

-- ==========
-- Employees
-- ==========

CREATE TABLE employee (
    employee_id     INT AUTO_INCREMENT PRIMARY KEY,
    address_id      INT NOT NULL,
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    gender          VARCHAR(20),
    salary          DECIMAL(10,2),
    ssn             VARCHAR(20) UNIQUE,
    employee_email  VARCHAR(100) NOT NULL UNIQUE,
    phone           VARCHAR(20),
    employee_role   ENUM('customer_support','admin','super_admin') NOT NULL,
    FOREIGN KEY (address_id) REFERENCES address(address_id)
		ON DELETE RESTRICT
);

CREATE TABLE account_audit (
    audit_id        INT AUTO_INCREMENT PRIMARY KEY,
    target_employee INT NOT NULL,
    performed_by    INT NOT NULL,
    action_type     VARCHAR(50) NOT NULL,
    action_time     DATETIME DEFAULT CURRENT_TIMESTAMP,
    note            TEXT,
    FOREIGN KEY (target_employee) REFERENCES employee(employee_id)
		ON DELETE RESTRICT,
    FOREIGN KEY (performed_by) REFERENCES employee(employee_id)
		ON DELETE RESTRICT
);

-- =====================
-- Book metadata
-- =====================

CREATE TABLE category (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name        VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE subcategory (
    subcategory_id 		INT AUTO_INCREMENT PRIMARY KEY,
    subcategory_name	VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE keyword (
    keyword_id INT AUTO_INCREMENT PRIMARY KEY,
    term       VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE author (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    author_name      VARCHAR(100) NOT NULL
);

-- =====
-- Book
-- =====

CREATE TABLE book (
    book_id          INT AUTO_INCREMENT PRIMARY KEY,
    category_id      INT NOT NULL,
    title            VARCHAR(150) NOT NULL,
    publisher        VARCHAR(100),
    published_date   DATE,
    edition          VARCHAR(20),
    book_language    VARCHAR(50),
    isbn13           CHAR(13) UNIQUE,
    isbn10           CHAR(10) UNIQUE,
    book_condition   VARCHAR(50),
    acquisition_type VARCHAR(50),
    price            DECIMAL(10,2),
    quantity         INT NOT NULL,
    weight           DECIMAL(10,2),
    book_format      VARCHAR(50),
    CHECK (quantity >= 0),
    CHECK (isbn13 IS NOT NULL OR isbn10 IS NOT NULL),
    CHECK (book_format IN ('Hardcover','Paperback','Ebook','Audiobook')),
    CHECK (book_condition IN ('New','Good','Fair','Poor')),
    CHECK (acquisition_type IN ('Purchase','Donation','Rental','Transfer')),
    CHECK (price >= 0),
    FOREIGN KEY (category_id) REFERENCES category(category_id)
		ON DELETE RESTRICT
);

CREATE TABLE book_author (
    book_id   INT NOT NULL,
    author_id INT NOT NULL,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES book(book_id)
		ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES author(author_id)
		ON DELETE RESTRICT
);

CREATE TABLE book_subcategory (
    book_id        INT NOT NULL,
    subcategory_id INT NOT NULL,
    PRIMARY KEY (book_id, subcategory_id),
    FOREIGN KEY (book_id) REFERENCES book(book_id)
		ON DELETE CASCADE,
    FOREIGN KEY (subcategory_id) REFERENCES subcategory(subcategory_id)
		ON DELETE RESTRICT
);

CREATE TABLE book_keyword (
    book_id    INT NOT NULL,
    keyword_id INT NOT NULL,
    PRIMARY KEY (book_id, keyword_id),
    FOREIGN KEY (book_id) REFERENCES book(book_id)
		ON DELETE CASCADE,
    FOREIGN KEY (keyword_id) REFERENCES keyword(keyword_id)
		ON DELETE RESTRICT
);

CREATE TABLE review (
    review_id   INT AUTO_INCREMENT PRIMARY KEY,
    student_id  INT NOT NULL,
    book_id     INT NOT NULL,
    rating      INT NOT NULL,
    rating_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    CHECK (rating BETWEEN 1 AND 5),
    FOREIGN KEY (student_id) REFERENCES student(student_id)
		ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES book(book_id)
		ON DELETE CASCADE
);

-- =====================
-- Courses & Books
-- =====================

CREATE TABLE course (
    course_id     INT AUTO_INCREMENT PRIMARY KEY,
    department_id INT NOT NULL,
    course_name          VARCHAR(100) NOT NULL,
    course_code          VARCHAR(20) NOT NULL,
    FOREIGN KEY (department_id) REFERENCES department(department_id)
		ON DELETE CASCADE,
	UNIQUE (department_id, course_code)
);

CREATE TABLE course_instructor (
    course_id     INT NOT NULL,
    instructor_id INT NOT NULL,
    taught_year   INT NOT NULL,
    semester      VARCHAR(20) NOT NULL,
    PRIMARY KEY (course_id, instructor_id, taught_year, semester),
    FOREIGN KEY (course_id) REFERENCES course(course_id)
		ON DELETE CASCADE,
    FOREIGN KEY (instructor_id) REFERENCES instructor(instructor_id)
		ON DELETE RESTRICT
);

CREATE TABLE course_book (
    course_id  INT NOT NULL,
    book_id    INT NOT NULL,
    usage_type VARCHAR(50),
    PRIMARY KEY (course_id, book_id),
    FOREIGN KEY (course_id) REFERENCES course(course_id)
		ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES book(book_id)
		ON DELETE RESTRICT
);

-- =====================
-- Tickets
-- =====================

CREATE TABLE ticket_category (
    ticket_category_id 		INT AUTO_INCREMENT PRIMARY KEY,
    ticket_category_name	VARCHAR(50) NOT NULL
);

CREATE TABLE ticket (
    ticket_id          INT AUTO_INCREMENT PRIMARY KEY,
    category_id        INT NOT NULL,
    created_by_student INT,
    created_by_cs      INT,
    resolved_by_admin  INT,
    created_at         DATETIME DEFAULT CURRENT_TIMESTAMP,
    title              VARCHAR(150) NOT NULL,
    date_completed     DATE,
    ticket_description VARCHAR(500),
    solution           VARCHAR(500),
    ticket_status      VARCHAR(30) NOT NULL,
    FOREIGN KEY (category_id) REFERENCES ticket_category(ticket_category_id)
		ON DELETE RESTRICT,
    FOREIGN KEY (created_by_student) REFERENCES student(student_id)
		ON DELETE SET NULL,
    FOREIGN KEY (created_by_cs) REFERENCES employee(employee_id)
		ON DELETE SET NULL,
    FOREIGN KEY (resolved_by_admin) REFERENCES employee(employee_id)
		ON DELETE SET NULL
);

CREATE TABLE ticket_state_history (
    history_id  INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id   INT NOT NULL,
    employee_id INT NOT NULL,
    old_status  VARCHAR(30),
    new_status  VARCHAR(30) NOT NULL,
    acted_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES ticket(ticket_id)
		ON DELETE CASCADE,
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id)
		ON DELETE RESTRICT
);

-- =====================
-- Cart & Orders
-- =====================

CREATE TABLE cart (
    cart_id      INT AUTO_INCREMENT PRIMARY KEY,
    student_id   INT NOT NULL UNIQUE,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    cart_status  VARCHAR(20) NOT NULL,
    CHECK (cart_status IN ('Active', 'CheckedOut', 'Closed')),
    FOREIGN KEY (student_id) REFERENCES student(student_id) 
		ON DELETE CASCADE
);

CREATE TABLE cart_item (
    cart_id    INT NOT NULL,
    book_id    INT NOT NULL,
    quantity   INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (cart_id, book_id),
    CHECK (quantity > 0),
    FOREIGN KEY (cart_id) REFERENCES cart(cart_id)
		ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES book(book_id)
		ON DELETE RESTRICT
);

-- original name: Order  -> implemented as customer_order
CREATE TABLE customer_order (
    order_id          INT AUTO_INCREMENT PRIMARY KEY,
    student_id        INT NOT NULL,
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    fulfilled_at      DATETIME,
    shipping_type     VARCHAR(30),
    credit_card_number VARCHAR(32),
    credit_card_exp   DATE,
    credit_card_name  VARCHAR(100),
    credit_card_type  VARCHAR(30),
    order_status      VARCHAR(30) NOT NULL,
    CHECK (shipping_type IN ('Standard', 'Express', 'Pickup')),
    CHECK (order_status IN ('Pending','Paid','Shipped','Cancelled','Completed')),
    FOREIGN KEY (student_id) REFERENCES student(student_id) 
		ON DELETE CASCADE
);

-- original name: Orderitem -> implemented as order_item
CREATE TABLE order_item (
    order_id   INT NOT NULL,
    book_id    INT NOT NULL,
    quantity   INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (order_id, book_id),
    CHECK (quantity > 0),
    FOREIGN KEY (order_id) REFERENCES customer_order(order_id)
		ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES book(book_id)
		ON DELETE RESTRICT
);

CREATE TABLE purchase_history (
	purchase_id	  BIGINT AUTO_INCREMENT PRIMARY KEY,
    student_id    INT NOT NULL,
    book_id       INT NOT NULL,
    order_id      INT NOT NULL,
    purchase_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id)
		ON DELETE RESTRICT,
    FOREIGN KEY (book_id) REFERENCES book(book_id)
		ON DELETE RESTRICT,
    FOREIGN KEY (order_id) REFERENCES customer_order(order_id)
		ON DELETE RESTRICT
);