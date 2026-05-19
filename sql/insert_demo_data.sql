-- ================================================================
--  BookFetch - Phase 4 Physical Design
--  insert_demo_data.sql
--
--  Demo dataset to support UI flows:
--    - Students browsing books by category/keyword
--    - Courses linked to required books
--    - Students adding books to cart and placing orders
--    - Reviews for books
--    - Support tickets created and updated by employees
--   - Account audit entries for admin actions
--
--  NOTE:
--    - This script assumes an empty book_fetch database where all
--      tables from create_tables.sql already exist.
--    - Primary keys are AUTO_INCREMENT, so we do NOT specify them in
--      INSERT statements. We rely on insertion order for FK values
--      (e.g., first student inserted has student_id = 1).
-- ================================================================

USE book_fetch;

-- ======================
-- Address data
-- ======================

INSERT INTO address (street, city, state, zip) VALUES
('10 Campus Way',      'St Paul',     'MN', '55105'),  -- id 1
('1 Aquinas Hall',     'St Paul',     'MN', '55105'),  -- id 2
('500 Admin Avenue',   'Minneapolis', 'MN', '55401');  -- id 3

-- ======================
-- University & Department
-- ======================

INSERT INTO university (address_id, university_name, rep_first_name, rep_last_name, rep_email, rep_phone) VALUES
(2, 'St Thomas University', 'Thomas', 'Aquinas', 'taquinas@stu.edu', '651-555-1000');  -- id 1

INSERT INTO department (university_id, department_name) VALUES
(1, 'Computer Science'),  -- 1
(1, 'Mathematics');       -- 2

-- ======================
-- Instructors
-- ======================

INSERT INTO instructor (university_id, department_id, first_name, last_name, email) VALUES
(1, 1, 'Reed', 'Thompson', 'rthompson@stu.edu'),
(1, 2, 'Walter', 'White', 'wwhite@stu.edu');

-- ======================
-- Students
-- ======================

INSERT INTO student (
    university_id, address_id, first_name, last_name,
    email, phone, birth_date, major, student_status,
    Student_year, username
) VALUES
(1, 1, 'John',  'Pork',    'jpork@stu.edu',  '651-555-2001',
 '2004-05-01', 'Computer Science', 'Full-time', 'Sophomore', 'jpork'),
(1, 1, 'Jesse', 'Pinkman', 'jpinkman@stu.edu','651-555-2002',
 '2003-09-15', 'Mathematics', 'Full-time', 'Junior', 'jpinkman');

-- ======================
-- Employees
-- ======================

INSERT INTO employee (
    address_id, first_name, last_name, gender,
    salary, ssn, employee_email, phone, employee_role
) VALUES
(3, 'John',   'Jones',     'M', 45000.00, '111-22-3333', 'jjones@bookfetch.com',   '612-555-3001', 'customer_support'),
(3, 'Connor', 'McGregor',  'M', 60000.00, '222-33-4444', 'cmcgregor@bookfetch.com','612-555-3002', 'admin'),
(3, 'Ilia',   'Topuria',   'M', 80000.00, '333-44-5555', 'itopuria@bookfetch.com', '612-555-3003', 'super_admin');

-- ======================
-- Account Audit
-- ======================

INSERT INTO account_audit (target_employee, performed_by, action_type, action_time, note) VALUES
(1, 3, 'CREATE_EMPLOYEE', NOW(), 'Super admin created customer_support employee John Jones.'),
(2, 3, 'PROMOTE_EMPLOYEE', NOW(), 'Super admin promoted Connor McGregor to admin.');

-- ======================
-- Book metadata
-- ======================

INSERT INTO category (category_name) VALUES
('Computer Science'),
('Mathematics');

INSERT INTO subcategory (subcategory_name) VALUES
('Algorithms'),
('Data Structures'),
('Discrete Math'),
('Databases');

INSERT INTO keyword (term) VALUES
('python'),
('database'),
('discrete math'),
('intro'),
('sql');

INSERT INTO author (author_name) VALUES
('Thomas H. Cormen'),
('Robert Sedgewick'),
('Kenneth Rosen'),
('Silberschatz, Korth, and Sudarshan');

-- ======================
-- Books
-- ======================

INSERT INTO book (
    category_id, title, publisher, published_date,
    edition, book_language, isbn13, isbn10, book_condition,
    acquisition_type, price, quantity, weight, book_format
) VALUES
(1, 'Introduction to Algorithms', 'MIT Press', '2009-01-01',
 '3', 'English', '9780262033848', '0262033844', 'New',
 'Purchase', 120.00, 5, 2.5, 'Hardcover'),

(1, 'Algorithms, 4th Edition', 'Addison-Wesley', '2011-01-01',
 '4', 'English', '9780321573513', '032157351X', 'Good',
 'Donation', 90.00, 3, 2.0, 'Hardcover'),

(2, 'Discrete Mathematics and Its Applications', 'McGraw-Hill', '2018-01-01',
 '8', 'English', '9781259676512', '125967651X', 'New',
 'Purchase', 150.00, 4, 2.8, 'Hardcover'),

(1, 'Database System Concepts', 'McGraw-Hill', '2010-01-01',
 '6', 'English', '9780073523323', '0073523321', 'Fair',
 'Purchase', 110.00, 2, 2.3, 'Hardcover');

-- BOOK RELATION TABLES

INSERT INTO book_author (book_id, author_id) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 4);

INSERT INTO book_subcategory (book_id, subcategory_id) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 4);

INSERT INTO book_keyword (book_id, keyword_id) VALUES
(1, 4),
(2, 1),
(3, 3),
(4, 2),
(4, 5);

-- ======================
-- Reviews
-- ======================

INSERT INTO review (student_id, book_id, rating, rating_date) VALUES
(1, 1, 5, NOW()),
(1, 4, 4, NOW()),
(2, 3, 4, NOW());

-- ======================
-- Courses
-- ======================

INSERT INTO course (department_id, course_name, course_code) VALUES
(1, 'Data Structures & Algorithms', 'CISC 340'),
(1, 'Database Systems', 'CISC 450'),
(2, 'Discrete Mathematics', 'MATH 128');

INSERT INTO course_instructor (course_id, instructor_id, taught_year, semester) VALUES
(1, 1, 2025, 'Spring'),
(2, 1, 2025, 'Fall'),
(3, 2, 2025, 'Spring');

INSERT INTO course_book (course_id, book_id, usage_type) VALUES
(1, 1, 'Required'),
(1, 2, 'Recommended'),
(2, 4, 'Required'),
(3, 3, 'Required');

-- ======================
-- Tickets
-- ======================

INSERT INTO ticket_category (ticket_category_name) VALUES
('Account Issue'),
('Missing Book'),
('Order Problem');

INSERT INTO ticket (
    category_id, created_by_student, created_by_cs,
    resolved_by_admin, created_at, title,
    date_completed, ticket_description, solution, ticket_status
) VALUES
(1, 1, NULL, NULL, NOW(), 'Cannot log in',
 NULL, 'Student John Pork cannot log into BookFetch.', NULL, 'Open'),

(2, 2, 1, 2, NOW(), 'Requested title not found',
 CURDATE(),
 'Student Jesse Pinkman cannot find a discrete math workbook.',
 'Support logged issue and admin added an alternate resource.',
 'Resolved');

INSERT INTO ticket_state_history (ticket_id, employee_id, old_status, new_status, acted_at) VALUES
(1, 1, NULL, 'Open', NOW()),
(2, 1, 'Open', 'In Progress', NOW()),
(2, 2, 'In Progress', 'Resolved', NOW());

-- ======================
-- Cart & Items
-- ======================

INSERT INTO cart (student_id, date_created, date_updated, cart_status) VALUES
(1, NOW(), NOW(),'Active'),
(2, NOW(), NOW(),'Active');

INSERT INTO cart_item (cart_id, book_id, quantity, unit_price) VALUES
(1, 1, 1, 120.00),
(1, 4, 1, 110.00),
(2, 3, 1, 150.00);

-- ======================
-- Orders
-- ======================

INSERT INTO customer_order (
    student_id, created_at, fulfilled_at,
    shipping_type, credit_card_number, credit_card_exp,
    credit_card_name, credit_card_type, order_status
) VALUES
(1, NOW(), NOW(), 'Standard',
 '4111111111111111', '2030-12-27', 'John Pork', 'Visa', 'Completed');

INSERT INTO order_item (order_id, book_id, quantity, unit_price) VALUES
(1, 1, 1, 120.00),
(1, 4, 1, 110.00);

INSERT INTO purchase_history (student_id, book_id, order_id, purchase_date) VALUES
(1, 1, 1, NOW()),
(1, 4, 1, NOW());