-- ================================================================
--  BookFetch - Phase 4 Physical Design
--  delete_demo_data.sql
--
--  Deletes demo data inserted by insert_demo_data.sql.
--  Tables are cleared in dependency-safe order to avoid FK errors.
-- ================================================================

USE book_fetch;
SET SQL_SAFE_UPDATES = 0;

-- ============================
-- Delete dependent relationships
-- ============================

-- Ordering-related
DELETE FROM purchase_history;
DELETE FROM order_item;
DELETE FROM customer_order;

-- Cart-related
DELETE FROM cart_item;
DELETE FROM cart;

-- Ticket system
DELETE FROM ticket_state_history;
DELETE FROM ticket;
DELETE FROM ticket_category;

-- Courses
DELETE FROM course_book;
DELETE FROM course_instructor;
DELETE FROM course;

-- Reviews
DELETE FROM review;

-- Book metadata relations
DELETE FROM book_keyword;
DELETE FROM book_subcategory;
DELETE FROM book_author;

-- Independent book metadata
DELETE FROM book;
DELETE FROM author;
DELETE FROM keyword;
DELETE FROM subcategory;
DELETE FROM category;

-- Account logs (must delete before employees)
DELETE FROM account_audit;

-- Core entities
DELETE FROM employee;
DELETE FROM student;
DELETE FROM instructor;
DELETE FROM department;
DELETE FROM university;

-- Root table
DELETE FROM address;

-- ================================================================
-- Reset AUTO_INCREMENT values
-- insert_demo_data.sql assumes IDs start from 1.
-- ================================================================

ALTER TABLE address             AUTO_INCREMENT = 1;
ALTER TABLE university          AUTO_INCREMENT = 1;
ALTER TABLE department          AUTO_INCREMENT = 1;

ALTER TABLE instructor          AUTO_INCREMENT = 1;
ALTER TABLE student             AUTO_INCREMENT = 1;
ALTER TABLE employee            AUTO_INCREMENT = 1;

ALTER TABLE account_audit       AUTO_INCREMENT = 1;

ALTER TABLE category            AUTO_INCREMENT = 1;
ALTER TABLE subcategory         AUTO_INCREMENT = 1;
ALTER TABLE keyword             AUTO_INCREMENT = 1;
ALTER TABLE author              AUTO_INCREMENT = 1;
ALTER TABLE book                AUTO_INCREMENT = 1;
ALTER TABLE review              AUTO_INCREMENT = 1;

ALTER TABLE course              AUTO_INCREMENT = 1;
ALTER TABLE course_instructor   AUTO_INCREMENT = 1;
ALTER TABLE course_book         AUTO_INCREMENT = 1;

ALTER TABLE ticket_category     AUTO_INCREMENT = 1;
ALTER TABLE ticket              AUTO_INCREMENT = 1;
ALTER TABLE ticket_state_history AUTO_INCREMENT = 1;

ALTER TABLE cart                AUTO_INCREMENT = 1;
ALTER TABLE cart_item           AUTO_INCREMENT = 1;

ALTER TABLE customer_order      AUTO_INCREMENT = 1;
ALTER TABLE order_item          AUTO_INCREMENT = 1;
ALTER TABLE purchase_history    AUTO_INCREMENT = 1;