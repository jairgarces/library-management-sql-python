import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from mysql.connector import Error

# Map report numbers to SQL strings (reports 1–22)
REPORT_QUERIES = {
    "1": """
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
    """,
    "2": """
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
    """,
    "3": """
        SELECT s.*
        FROM student s
        JOIN customer_order co
            ON s.student_id = co.student_id
        JOIN order_item oi
            ON co.order_id = oi.order_id
        WHERE s.major = 'Computer Science'
        GROUP BY s.student_id, s.first_name, s.last_name, s.email, s.major
        HAVING SUM(oi.quantity) / COUNT(DISTINCT co.order_id) > 2;
    """,
    "4": """
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
    """,
    "5": """
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
    """,
    "6": """
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
    """,
    "7": """
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
    """,
    "8": """
        SELECT 
            b.title,
            b.book_id,
            COUNT(c.course_id) AS course_count
        FROM book as b
        JOIN course_book as cb ON cb.book_id = b.book_id
        JOIN course as c ON c.course_id = cb.course_id
        GROUP BY b.book_id, b.title
        ORDER BY course_count DESC;
    """,
    "9": """
        SELECT DISTINCT b.title
        FROM book as b
        JOIN course_book cb ON cb.book_id = b.book_id
        JOIN course c ON cb.course_id = c.course_id
        WHERE c.course_name = 'Linear Algebra'
        ORDER BY b.title;
    """,
    "10": """
        SELECT 
            b.title,
            AVG(r.rating) AS Average_Rating
        FROM book as b
        JOIN review as r ON r.book_id = b.book_id
        GROUP BY b.book_id, b.title
        HAVING AVG(r.rating) > 3
        ORDER BY Average_Rating DESC;
    """,
    "11": """
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
    """,
    "12": """
        SELECT 
            c.category_name,
            count(ph.book_id) / COUNT(DISTINCT ph.student_id) AS avg_books_per_student
        FROM category c
        JOIN book b ON b.category_id = c.category_id
        JOIN purchase_history ph ON ph.book_id = b.book_id
        GROUP BY c.category_name
        ORDER BY avg_books_per_student DESC;
    """,
    "13": """
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
    """,
    "14": """
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
    """,
    "15": """
        SELECT 
            e.employee_id,
            CONCAT(e.first_name, ' ', e.last_name) AS cs_name,
            COUNT(t.ticket_id) AS tickets_created
        FROM employee e
        LEFT JOIN ticket t ON t.created_by_cs = e.employee_id
        WHERE e.employee_role = 'customer_support'
        GROUP BY e.employee_id, e.first_name, e.last_name
        ORDER BY tickets_created DESC;
    """,
    "16": """
        SELECT 
            CONCAT(e.first_name, ' ', e.last_name) AS admin_name,
            e.salary
        FROM employee e
        WHERE e.employee_role IN ('admin','super_admin')
        ORDER BY e.salary DESC;
    """,
    "17": """
        SELECT 
            CONCAT(e.first_name, ' ', e.last_name) AS admin_name,
            SUM(CASE WHEN t.ticket_status = 'Resolved' THEN 1 ELSE 0 END) AS tickets_closed
        FROM employee e
        LEFT JOIN ticket t ON t.resolved_by_admin = e.employee_id
        WHERE e.employee_role IN ('admin','super_admin')
        GROUP BY e.employee_id, e.first_name, e.last_name
        ORDER BY tickets_closed DESC;
    """,
    "18": """
        SELECT 
            t.ticket_status AS state,
            COUNT(t.ticket_id) AS total_tickets,
            SUM(CASE WHEN t.created_by_student IS NOT NULL THEN 1 ELSE 0 END) AS created_by_students,
            SUM(CASE WHEN t.created_by_cs IS NOT NULL THEN 1 ELSE 0 END) AS created_by_cs
        FROM ticket t
        GROUP BY state
        ORDER BY state;
    """,
    "19": """
        SELECT 
            AVG(TIMESTAMPDIFF(
                SECOND,
                t.created_at,
                CONCAT(t.date_completed, ' 00:00:00')
            )) / 3600 AS avg_duration_hours
        FROM ticket t
        WHERE t.date_completed IS NOT NULL;
    """,
    "20": """
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
    """,
    "21": """
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
    """,
    "22": """
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
    """,
    "23": """
        SELECT 
            b.title,
            b.book_id,
            AVG(r.rating) AS avg_rating,
            COUNT(DISTINCT r.student_id) AS num_students_rated
        FROM book b
        LEFT JOIN review r ON r.book_id = b.book_id
        GROUP BY b.book_id, b.title
        ORDER BY avg_rating DESC;
    """,
    "24": """
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
    """,
    "25": """
        SELECT 
            c.category_name,
            b.title,
            b.book_id,
            b.quantity
        FROM book b
        JOIN category c ON c.category_id = b.category_id
        WHERE b.quantity < 4
        ORDER BY c.category_name, b.quantity ASC;
    """,
    "26": """
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
    """,
    "27": """
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
    """,
    "28": """
        SELECT
            b.book_id,
            b.title,
            AVG(CASE WHEN r.rating_date >= NOW() - INTERVAL 30 DAY THEN r.rating END) AS avg_last30,
            AVG(CASE WHEN r.rating_date >= NOW() - INTERVAL 60 DAY
                     AND r.rating_date < NOW() - INTERVAL 30 DAY THEN r.rating END) AS avg_prev30,
            (AVG(CASE WHEN r.rating_date >= NOW() - INTERVAL 30 DAY THEN r.rating END)
             - AVG(CASE WHEN r.rating_date >= NOW() - INTERVAL 60 DAY
                         AND r.rating_date < NOW() - INTERVAL 30 DAY THEN r.rating END)) AS d
        FROM book b
        JOIN review r ON r.book_id = b.book_id
        GROUP BY b.book_id, b.title
        HAVING d >= 1
        ORDER BY d DESC;
    """,
    "29": """
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
    """,
    "30": """
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
    """,
    "31": """
        SELECT
            c.category_name,
            SUM(b.quantity) AS total_on_hand,
            SUM(b.quantity * COALESCE(b.price,0)) AS total_inventory_value
        FROM category c
        JOIN book b ON b.category_id = c.category_id
        GROUP BY c.category_id, c.category_name
        ORDER BY total_inventory_value DESC;
    """,
    "32": """
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
    """,
    "33": """
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
    """,
    "34": """
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
    """,
    "35": """
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
    """,

}

class ReportsModule(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Reports")
        self.geometry("900x500")

        # Top section: input and button
        top_frame = tk.Frame(self)
        top_frame.pack(fill="x", pady=10, padx=10)

        tk.Label(top_frame, text="Report Number:").pack(side="left", padx=(0, 5))

        self.report_num_entry = tk.Entry(top_frame, width=10)
        self.report_num_entry.pack(side="left", padx=(0, 10))

        run_btn = tk.Button(top_frame, text="Run Report", command=self.run_report)
        run_btn.pack(side="left")

        # Status label
        self.status_label = tk.Label(self, text="", anchor="w", fg="gray")
        self.status_label.pack(fill="x", padx=10)

        # Table area
        table_frame = tk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(table_frame, show="headings")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def clear_table(self):
        for col in self.tree["columns"]:
            self.tree.heading(col, text="")
        self.tree["columns"] = ()
        for row in self.tree.get_children():
            self.tree.delete(row)

    def run_report(self):
        report_num = self.report_num_entry.get().strip()

        if not report_num:
            messagebox.showerror("Error", "Please enter a report number.")
            return

        if report_num not in REPORT_QUERIES:
            messagebox.showerror(
                "Error",
                f"No query defined for report #{report_num}."
            )
            return

        sql = REPORT_QUERIES[report_num]

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []

            cursor.close()
            conn.close()

            self.status_label.config(
                text=f"Report {report_num}: {len(rows)} row(s) returned."
            )

            self.clear_table()

            if not columns:
                messagebox.showinfo("Info", "Query executed, but no columns were returned.")
                return

            self.tree["columns"] = columns
            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=120, anchor="w")

            for row in rows:
                self.tree.insert("", "end", values=row)

        except Error as e:
            messagebox.showerror("Database Error", str(e))
