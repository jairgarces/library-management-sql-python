USE book_fetch;

 /* 1. List the details of students attending 'UST'. */
SELECT s.student_id,
       s.username,
       s.first_name,
       s.last_name,
       s.email,
       s.phone,
       s.birth_date,
       s.major,
       s.student_status,
       s.Student_year,
       u.university_name
FROM student AS s
JOIN university AS u
  ON s.university_id = u.university_id
WHERE u.university_name = 'St Thomas University'
ORDER BY s.last_name, s.first_name;

 /* 2. List the details of students from all universities who are graduate students. */
SELECT s.student_id,
       s.username,
       s.first_name,
       s.last_name,
       s.email,
       s.phone,
       s.birth_date,
       s.major,
       s.student_status,
       s.Student_year,
       u.university_name
FROM student AS s
JOIN university AS u
  ON s.university_id = u.university_id
WHERE s.student_status = 'Graduate'
ORDER BY u.university_name, s.last_name, s.first_name;

-- 3. List the details of students majoring in “Computer Science” and buying, on average, more than two books. – Student attributes
SELECT
    s.*
FROM student s
JOIN customer_order co
    ON s.student_id = co.student_id
JOIN order_item oi
    ON co.order_id = oi.order_id
WHERE s.major = 'Computer Science'
GROUP BY s.student_id, s.first_name, s.last_name, s.email, s.major
HAVING SUM(oi.quantity) / COUNT(DISTINCT co.order_id) > 2;

-- 4. List the books that have sold the most or that have been rented the most. – Book title, book PK
SELECT 
    b.book_id,
    b.title,
    SUM(CASE WHEN b.acquisition_type = 'Rental' THEN oi.quantity ELSE 0 END) AS total_rented,
    SUM(CASE WHEN b.acquisition_type = 'Purchase' THEN oi.quantity ELSE 0 END) AS total_sold
FROM book as b
JOIN order_item as oi ON b.book_id = oi.book_id
JOIN customer_order as co ON oi.order_id = co.order_id
GROUP BY b.book_id, b.title
ORDER BY GREATEST(total_sold, total_rented) DESC
LIMIT 10;
-- 5. List, by category and subcategory, all the books. – Category, subcategory, book title, book PK
SELECT 
    c.category_name,
    sc.subcategory_name,
    b.title,
    b.book_id
FROM book as b
JOIN category as c 
    ON b.category_id = c.category_id
JOIN book_subcategory as bs 
    ON b.book_id = bs.book_id
JOIN subcategory as sc 
    ON bs.subcategory_id = sc.subcategory_id
ORDER BY c.category_name, sc.subcategory_name, b.title;

-- 6. List all the book names required for a course, excluding books in the “Computer Science” category. – Course name, book title
SELECT 
    c.course_name,
    b.title
FROM course as c
JOIN course_book as cb 
    ON c.course_id = cb.course_id
JOIN book as b 
    ON cb.book_id = b.book_id
JOIN category as cat
    ON b.category_id = cat.category_id
WHERE cat.category_name <> 'Computer Science'
ORDER BY c.course_name, b.title;
-- 7. List all the books bought by students not associated with a course at a university that have at least two keywords in common with books associated with a university. – Book title, book PK
SELECT 
    b.title,
    b.book_id
FROM book as b
JOIN book_keyword as bk ON b.book_id = bk.book_id
JOIN keyword as kw ON kw.keyword_id = bk.keyword_id
JOIN purchase_history as ph ON ph.book_id = b.book_id
WHERE b.book_id NOT IN (
    SELECT cb.book_id 
    FROM course_book cb
)
AND b.book_id IN (
    SELECT b2.book_id
    FROM book as b2
    JOIN book_keyword as bk2 ON b2.book_id = bk2.book_id
    JOIN course_book as cb2 ON cb2.book_id = b2.book_id
    GROUP BY b2.book_id
    HAVING COUNT(DISTINCT bk2.keyword_id) >= 2
)
GROUP BY b.book_id, b.title
ORDER BY b.title;
-- 8. List all the books together with a count of the number of courses each book has been associated with. – Book title, book PK, count of courses
SELECT 
    b.title,
    b.book_id,
    COUNT(c.course_id) AS course_count
FROM book as b
JOIN course_book as cb ON cb.book_id = b.book_id
JOIN course as c ON c.course_id = cb.course_id
GROUP BY b.book_id, b.title
ORDER BY course_count DESC;

-- 9. List the book titles that are related to 'Linear Algebra'. – Book title
SELECT DISTINCT b.title
FROM book as b
JOIN course_book cb ON cb.book_id = b.book_id
JOIN course c ON cb.course_id = c.course_id
WHERE c.course_name = 'Linear Algebra'
ORDER BY b.title;

-- 10. List the books with overall ratings higher than 3. – Book title
SELECT 
    b.title,
    AVG(r.rating) AS Average_Rating
FROM book as b
JOIN review as r ON r.book_id = b.book_id
GROUP BY b.book_id, b.title
HAVING AVG(r.rating) > 3
ORDER BY Average_Rating DESC;

-- 11. Show, for each book, the number of purchases (orders) made and the overall rating, ordered by rating, and include books without ratings. – Book title, count of purchases (orders), overall rating (aggregate)
SELECT 
    b.title,
    b.book_id,
    AVG(r.rating) AS average_rating,
    COUNT(ph.purchase_id) AS purchase_count
FROM book as b
LEFT JOIN review as r ON r.book_id = b.book_id
LEFT JOIN purchase_history as ph ON ph.book_id = b.book_id
GROUP BY b.book_id, b.title
ORDER BY average_rating DESC;

-- 12. List the average number (quantity) of books students buy, grouped by book category
-- . – Category, average number of books
SELECT 
    c.category_name,
    count(ph.book_id) / COUNT(DISTINCT ph.student_id) AS avg_books_per_student
FROM category c
JOIN book b ON b.category_id = c.category_id
JOIN purchase_history ph ON ph.book_id = b.book_id
GROUP BY c.category_name
ORDER BY avg_books_per_student DESC;


-- 13. List the details of each university, including departments, courses, and the number of instructors per course. – University name, department name, course name, count of instructors per course
SELECT 
    u.university_name,
    d.department_name,
    c.course_name,
    COUNT(ci.instructor_id) AS num_instructors
FROM university u
JOIN department d ON d.university_id = u.university_id
JOIN course c ON c.department_id = d.department_id
LEFT JOIN course_instructor ci ON ci.course_id = c.course_id
GROUP BY d.department_id, c.course_id
ORDER BY u.university_name, d.department_name, c.course_name;
-- 14. For each university, find the total number of books associated with that university and the total sum of book costs, filtering out purchases by students who do not belong to that university. – University name, count of books, total sum of book costs
SELECT 
    u.university_name,
    COUNT(DISTINCT ph.book_id) AS total_books,
    SUM(b.price) AS total_book_cost
FROM university u
JOIN student s ON s.university_id = u.university_id
JOIN purchase_history ph ON ph.student_id = s.student_id
JOIN book b ON b.book_id = ph.book_id
GROUP BY u.university_id, u.university_name
ORDER BY u.university_name;

-- 15. List each customer support employee and the total number of tickets they created. – CS name and PK, count of tickets created
SELECT 
    e.employee_id,
    CONCAT(e.first_name, ' ', e.last_name) AS cs_name,
    COUNT(t.ticket_id) AS tickets_created
FROM employee e
LEFT JOIN ticket t ON t.created_by_cs = e.employee_id
WHERE e.employee_role = 'customer_support'
GROUP BY e.employee_id, e.first_name, e.last_name
ORDER BY tickets_created DESC;

-- 16. List the names of administrators, ordered by salary. – Admin name, salary (ordered)
SELECT 
    CONCAT(e.first_name, ' ', e.last_name) AS admin_name,
    e.salary
FROM employee e
WHERE e.employee_role IN ('admin','super_admin')
ORDER BY e.salary DESC;

-- 17. List the administrators’ names together with the total number of tickets they have closed.– Admin name, count of tickets closed
SELECT 
    CONCAT(e.first_name, ' ', e.last_name) AS admin_name,
    SUM(CASE WHEN t.ticket_status = 'Resolved' THEN 1 ELSE 0 END) AS tickets_closed
FROM employee e
LEFT JOIN ticket t ON t.resolved_by_admin = e.employee_id
WHERE e.employee_role IN ('admin','super_admin')
GROUP BY e.employee_id, e.first_name, e.last_name
ORDER BY tickets_closed DESC;

-- 18. List the tickets grouped by their state, including the total number created by students and the total number created by customer support. – State, total number
SELECT 
    t.ticket_status AS state,
    COUNT(t.ticket_id) AS total_tickets,
    SUM(CASE WHEN t.created_by_student IS NOT NULL THEN 1 ELSE 0 END) AS created_by_students,
    SUM(CASE WHEN t.created_by_cs IS NOT NULL THEN 1 ELSE 0 END) AS created_by_cs
FROM ticket t
GROUP BY state
ORDER BY state;

-- 19. Find the average time for a ticket from created to closed. – Average duration Database Design I
SELECT 
    AVG(TIMESTAMPDIFF(
        SECOND,
        t.created_at,
        CONCAT(t.date_completed, ' 00:00:00')
    )) / 3600 AS avg_duration_hours
FROM ticket t
WHERE t.date_completed IS NOT NULL;
-- 20. For each ticket that is closed, show the ticket history ordered by timestamp. – Ticket title/PK, ticket attributes, including state
SELECT 
    t.ticket_id,
    t.title,
    h.history_id,
    h.old_status,
    h.new_status,
    h.acted_at
FROM ticket t
JOIN ticket_state_history h ON h.ticket_id = t.ticket_id
WHERE t.ticket_status = 'Closed'
ORDER BY t.ticket_id, h.acted_at;

-- 21. List the recommended books for each student based on the defined recommendation rules. – Student name, recommended book titles
SELECT 
    s.student_id,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    b2.title AS recommended_book
FROM student s
JOIN purchase_history ph ON ph.student_id = s.student_id
JOIN book_keyword bk ON bk.book_id = ph.book_id
JOIN keyword k ON k.keyword_id = bk.keyword_id
JOIN book_keyword bk2 ON bk2.keyword_id = k.keyword_id
JOIN book b2 ON b2.book_id = bk2.book_id
WHERE b2.book_id NOT IN (
    SELECT book_id 
    FROM purchase_history 
    WHERE student_id = s.student_id
)
GROUP BY s.student_id, b2.book_id;

-- 22. For each book, list the total count of students who have purchased (ordered) other books with at least one keyword in common (excluding the current book). – Book title, count of students
SELECT 
    b.title,
    b.book_id,
    COUNT(DISTINCT ph.student_id) AS student_count
FROM book b
JOIN book_keyword bk ON bk.book_id = b.book_id
JOIN book_keyword bk2 
    ON bk2.keyword_id = bk.keyword_id 
   AND bk2.book_id <> b.book_id
JOIN purchase_history ph ON ph.book_id = bk2.book_id
GROUP BY b.book_id, b.title
ORDER BY student_count DESC;

-- 23. List the books by overall ratings and by the number of students who rated them. – Rating, book titles, number of students who rated each book
SELECT 
    b.title,
    b.book_id,
    AVG(r.rating) AS avg_rating,
    COUNT(DISTINCT r.student_id) AS num_students_rated
FROM book b
LEFT JOIN review r ON r.book_id = b.book_id
GROUP BY b.book_id, b.title
ORDER BY avg_rating DESC;

-- 24. List the books with a rating of 5 (not averaged across ratings) and the students who rated the books, along with the students’ universities. – Book title, rating, student name, university name
SELECT 
    b.title,
    r.rating,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    u.university_name
FROM review r
JOIN book b ON b.book_id = r.book_id
JOIN student s ON s.student_id = r.student_id
JOIN university u ON u.university_id = s.university_id
WHERE r.rating = 5
ORDER BY b.title, student_name;

-- 25. List the books that are low in stock (quantity < 4), grouped by category, and ordered by quantity ascending. – Category, book title, book PK, quantity
SELECT 
    c.category_name,
    b.title,
    b.book_id,
    b.quantity
FROM book b
JOIN category c ON c.category_id = b.category_id
WHERE b.quantity < 4
ORDER BY c.category_name, b.quantity ASC;

-- 26. List the revenue by university and academic term by summing OrderItem.unit_price_at_order × quantity for orders placed by students of that university, grouped by university, term, and year. – University name, term, year, total revenue
SELECT
    u.university_name,
    CASE
        WHEN MONTH(co.created_at) IN (1,2,3,4,5) THEN 'Spring'
        WHEN MONTH(co.created_at) IN (6,7,8) THEN 'Summer'
        ELSE 'Fall'
    END AS term,
    YEAR(co.created_at) AS year,
    SUM(oi.unit_price * oi.quantity) AS total_revenue
FROM university u
JOIN student s ON s.university_id = u.university_id
JOIN customer_order co ON co.student_id = s.student_id
JOIN order_item oi ON oi.order_id = co.order_id
GROUP BY u.university_id, term, YEAR(co.created_at), u.university_name
ORDER BY u.university_name, year, term;

-- 27. List the top-trending books in the last 30 days based on the total number of orders (purchases plus rentals). – Book title, book PK, total orders in last 30 days
SELECT
    b.book_id,
    b.title,
    COALESCE(SUM(oi.quantity), 0) AS total_orders_30_days
FROM book b
LEFT JOIN order_item oi
    ON oi.book_id = b.book_id
LEFT JOIN customer_order co
    ON co.order_id = oi.order_id
    AND co.created_at >= NOW() - INTERVAL 30 DAY
GROUP BY b.book_id, b.title
ORDER BY total_orders_30_days DESC
LIMIT 10;

-- 28. List the books whose average rating has increased by at least 1.0 when comparing the last 30 days to the prior 30 days. – Book title, average rating (last 30 days), average rating (previous 30 days), delta
SELECT
    b.book_id,
    b.title,
    AVG(CASE WHEN r.rating_date >= NOW() - INTERVAL 30 DAY THEN r.rating END)        AS avg_last30,
    AVG(CASE WHEN r.rating_date >= NOW() - INTERVAL 60 DAY
             AND r.rating_date <  NOW() - INTERVAL 30 DAY THEN r.rating END)        AS avg_prev30,
    (AVG(CASE WHEN r.rating_date >= NOW() - INTERVAL 30 DAY THEN r.rating END)
     - AVG(CASE WHEN r.rating_date >= NOW() - INTERVAL 60 DAY
                 AND r.rating_date < NOW() - INTERVAL 30 DAY THEN r.rating END)
    ) AS d
FROM book b
JOIN review r ON r.book_id = b.book_id
GROUP BY b.book_id, b.title
HAVING d >= 1
ORDER BY d DESC;

-- 29. List the carts created in the last 7 days that did not result in an order within 48 hours (abandoned carts). – Cart PK, student name/PK, date created, item count
SELECT
    c.cart_id,
    c.student_id,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    c.date_created,
    COALESCE(SUM(ci.quantity), 0) AS item_count
FROM cart c
JOIN student s ON s.student_id = c.student_id
LEFT JOIN cart_item ci ON ci.cart_id = c.cart_id
LEFT JOIN customer_order co
    ON co.student_id = c.student_id
   AND co.created_at <= c.date_created + INTERVAL 48 HOUR
WHERE c.date_created >= NOW() - INTERVAL 7 DAY
  AND co.order_id IS NULL
GROUP BY c.cart_id, c.student_id, c.date_created, s.first_name, s.last_name
ORDER BY c.date_created DESC;

-- 30. List, for the last 30 days, the conversion from cart additions to orders, grouped by category. – Category, cart additions count, orders count, conversion rate
SELECT
    c.category_name,
    COALESCE(cart_adds.cart_additions, 0) AS cart_additions,
    COALESCE(ord.orders, 0) AS orders,
    CASE WHEN COALESCE(cart_adds.cart_additions,0) = 0 THEN 0
         ELSE COALESCE(ord.orders,0) / COALESCE(cart_adds.cart_additions,0)
    END AS conversion_rate
FROM category c
LEFT JOIN (
    SELECT b.category_id, COUNT(DISTINCT ci.cart_id, ci.book_id) AS cart_additions
    FROM cart_item ci
    JOIN cart ca ON ca.cart_id = ci.cart_id
    JOIN book b ON b.book_id = ci.book_id
    WHERE ca.date_created >= NOW() - INTERVAL 30 DAY
    GROUP BY b.category_id
) AS cart_adds ON cart_adds.category_id = c.category_id
LEFT JOIN (
    SELECT b.category_id, SUM(oi.quantity) AS orders
    FROM order_item oi
    JOIN customer_order co ON co.order_id = oi.order_id
    JOIN book b ON b.book_id = oi.book_id
    WHERE co.created_at >= NOW() - INTERVAL 30 DAY
    GROUP BY b.category_id
) AS ord ON ord.category_id = c.category_id
ORDER BY c.category_name;

-- 31. List the inventory valuation by category by summing on-hand quantity and extended value (price × quantity). – Category, total on-hand quantity, total inventory value
SELECT
    c.category_name,
    SUM(b.quantity) AS total_on_hand,
    SUM(b.quantity * COALESCE(b.price,0)) AS total_inventory_value
FROM category c
JOIN book b ON b.category_id = c.category_id
GROUP BY c.category_id, c.category_name
ORDER BY total_inventory_value DESC;

-- 32. List the monthly distribution of digital (ebook) versus physical (hardcover/paperback) items. – Month, format group (ebook vs. physical), item quantity, percent of total
SELECT
    month,
    format_group,
    item_count,
    ROUND(item_count * 100.0 / total_for_month, 2) AS percent_of_total
FROM (
    SELECT
        DATE_FORMAT(ph.purchase_date, '%Y-%m') AS month,
        CASE WHEN b.book_format = 'Ebook' THEN 'ebook' ELSE 'physical' END AS format_group,
        COUNT(*) AS item_count,
        SUM(COUNT(*)) OVER (PARTITION BY DATE_FORMAT(ph.purchase_date, '%Y-%m')) AS total_for_month
    FROM purchase_history ph
    JOIN book b ON b.book_id = ph.book_id
    GROUP BY month, format_group
) t
ORDER BY month DESC, format_group;

-- 33. List the courses that have no associated book for the specified term and year. – University name, department name, course name, term, year
SELECT
    u.university_name,
    d.department_name,
    c.course_name
FROM course c
JOIN department d ON d.department_id = c.department_id
JOIN university u ON u.university_id = d.university_id
LEFT JOIN course_book cb ON cb.course_id = c.course_id
WHERE cb.book_id IS NULL
ORDER BY u.university_name, d.department_name, c.course_name;

-- 34. List the books that are associated with the greatest number of distinct universities, ordered by that count in descending order. – Book title, book PK, university count
SELECT
    b.book_id,
    b.title,
    COUNT(DISTINCT u.university_id) AS university_count
FROM book b
JOIN course_book cb ON cb.book_id = b.book_id
JOIN course c ON c.course_id = cb.course_id
JOIN department d ON d.department_id = c.department_id
JOIN university u ON u.university_id = d.university_id
GROUP BY b.book_id, b.title
ORDER BY university_count DESC, b.title
LIMIT 10;

-- 35. List, for each closed ticket, the number of state transitions recorded and indicate whether the ticket was reopened (moved back to a prior state). – Ticket title/PK, transition count, reopened flag
SELECT
    t.ticket_id,
    t.title,
    COUNT(h.history_id) AS transition_count,
    MAX(CASE WHEN h.new_status = 'Reopened' THEN 1 ELSE 0 END) AS reopened_flag
FROM ticket t
LEFT JOIN ticket_state_history h ON h.ticket_id = t.ticket_id
WHERE t.ticket_status = 'Closed'
GROUP BY t.ticket_id, t.title
ORDER BY transition_count DESC;
