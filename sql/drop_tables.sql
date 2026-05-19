-- ================================================================
--  BookFetch - Phase 4 Physical Design
--  drop_tables.sql
--
--  NOTE:
--  Tables must be dropped in reverse dependency order to avoid
--  foreign key constraint errors. This order mirrors the physical
--  schema created in create_tables.sql.
--
--  Dependency Overview:
--
--    • purchase_history references customer_order, student, and book,
--      so it must be dropped first.
--
--    • order_item references customer_order and book,
--      so it follows purchase_history.
--
--    • cart_item references cart and book,
--      so it must be dropped before cart.
--
--    • ticket_state_history references ticket and employee,
--      so it must be dropped before both.
--
--    • ticket references ticket_category, student, and employee,
--      so ticket must be dropped before its parents.
--
--    • course_book and course_instructor reference course, instructor,
--      and book, so they must be dropped before those tables.
--
--    • review references student and book,
--      so it must be dropped before both.
--
--    • book_author, book_subcategory, and book_keyword reference
--      book, author, subcategory, and keyword respectively.
--
--    • student and employee reference address,
--      so they must be dropped before address.
--
--    • department references university,
--      so it must be dropped before university.
--
--    • university references address,
--      so it must be dropped before address.
--
--    • address is the root table and must be dropped last.
-- ================================================================

USE book_fetch;

-- =========================
-- Purchase History
-- =========================
DROP TABLE IF EXISTS purchase_history;

-- =========================
-- Orders
-- =========================
DROP TABLE IF EXISTS order_item;
DROP TABLE IF EXISTS customer_order;

-- =========================
-- Cart
-- =========================
DROP TABLE IF EXISTS cart_item;
DROP TABLE IF EXISTS cart;

-- =========================
-- Ticketing System
-- =========================
DROP TABLE IF EXISTS ticket_state_history;
DROP TABLE IF EXISTS ticket;
DROP TABLE IF EXISTS ticket_category;

-- =========================
-- Courses & Instructors
-- =========================
DROP TABLE IF EXISTS course_book;
DROP TABLE IF EXISTS course_instructor;
DROP TABLE IF EXISTS course;
DROP TABLE IF EXISTS instructor;
DROP TABLE IF EXISTS department;

-- =========================
-- Reviews & Book Metadata
-- =========================
DROP TABLE IF EXISTS review;

DROP TABLE IF EXISTS book_keyword;
DROP TABLE IF EXISTS keyword;

DROP TABLE IF EXISTS book_subcategory;
DROP TABLE IF EXISTS subcategory;

DROP TABLE IF EXISTS book_author;
DROP TABLE IF EXISTS author;

DROP TABLE IF EXISTS book;
DROP TABLE IF EXISTS category;

-- =========================
-- Employees & Audit Logs
-- =========================
DROP TABLE IF EXISTS account_audit;
DROP TABLE IF EXISTS employee;

-- =========================
-- Students
-- =========================
DROP TABLE IF EXISTS student;

-- =========================
-- University
-- =========================
DROP TABLE IF EXISTS university;

-- =========================
-- Address (Root Table)
-- =========================
DROP TABLE IF EXISTS address;