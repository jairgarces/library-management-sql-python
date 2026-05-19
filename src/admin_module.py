import tkinter as tk
from tkinter import messagebox
from mysql.connector import Error

from db import get_connection


class AdminModule(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Administrator Module")
        self.geometry("650x1000")

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)

        self.content = tk.Frame(canvas)
        canvas.create_window((0, 0), window=self.content, anchor="nw")

        self.content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        self._build_book_section()
        self._build_university_section()
        self._build_ticket_section()
        self._build_course_book_section()

    # BOOK MANAGEMENT
    def _build_book_section(self):
        tk.Label(self.content, text="Book Management", font=("Helvetica", 16, "bold")).pack(pady=10)

        fields = [
            ("Title*", "title"),
            ("Category ID*", "category"),
            ("Publisher", "publisher"),
            ("Published Date (YYYY-MM-DD)", "published_date"),
            ("Edition", "edition"),
            ("Language", "language"),
            ("ISBN13*", "isbn13"),
            ("ISBN10", "isbn10"),
            ("Condition", "condition"),
            ("Acquisition Type", "acquisition"),
            ("Weight", "weight"),
            ("Price*", "price"),
            ("Quantity*", "qty"),
            ("Format", "format"),
        ]

        self.book_entries = {}

        for label, key in fields:
            row = tk.Frame(self.content)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label, width=30, anchor="w").pack(side="left")
            entry = tk.Entry(row, width=35)
            entry.pack(side="left")
            self.book_entries[key] = entry

        tk.Button(self.content, text="Create Book", command=self.create_book).pack(pady=6)
        tk.Button(self.content, text="Update Inventory (Price & Quantity ONLY)", command=self.update_inventory).pack(pady=4)
        tk.Button(self.content, text="Update Book Details (Partial)", command=self.update_book_details).pack(pady=6)

    def create_book(self):
        data = {k: e.get().strip() or None for k, e in self.book_entries.items()}

        if not data["title"]:
            messagebox.showerror("Error", "Title is required.")
            return
        if not data["category"]:
            messagebox.showerror("Error", "Category ID is required.")
            return
        if not (data["isbn13"] or data["isbn10"]):
            messagebox.showerror("Error", "ISBN13 or ISBN10 required.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO book (
                    category_id, title, publisher, published_date,
                    edition, book_language, isbn13, isbn10,
                    book_condition, acquisition_type,
                    price, quantity, weight, book_format
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                int(data["category"]),
                data["title"], data["publisher"], data["published_date"],
                data["edition"], data["language"],
                data["isbn13"], data["isbn10"],
                data["condition"], data["acquisition"],
                float(data["price"]), int(data["qty"]),
                float(data["weight"]) if data["weight"] else None,
                data["format"]
            ))

            conn.commit()
            messagebox.showinfo("Success", "Book created.")
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            cursor.close()
            conn.close()

    def update_inventory(self):
        isbn = self.book_entries["isbn13"].get() or self.book_entries["isbn10"].get()
        if not isbn:
            messagebox.showerror("Error", "ISBN required.")
            return

        try:
            price = float(self.book_entries["price"].get())
            qty = int(self.book_entries["qty"].get())
        except:
            messagebox.showerror("Error", "Price and Quantity must be valid numbers.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE book
                SET price = %s, quantity = %s
                WHERE isbn13 = %s OR isbn10 = %s
            """, (price, qty, isbn, isbn))

            conn.commit()
            messagebox.showinfo("Success", "Inventory updated.")
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            cursor.close()
            conn.close()

    def update_book_details(self):
        editable = {
            "publisher": "publisher",
            "published_date": "published_date",
            "edition": "edition",
            "language": "book_language",
            "condition": "book_condition",
            "format": "book_format",
            "acquisition": "acquisition_type",
            "weight": "weight",
        }

        updates, values = [], []

        for ui, db in editable.items():
            v = self.book_entries[ui].get().strip()
            if v:
                updates.append(f"{db} = %s")
                values.append(v)

        if not updates:
            messagebox.showwarning("Nothing to update", "No fields provided.")
            return

        isbn = self.book_entries["isbn13"].get() or self.book_entries["isbn10"].get()
        if not isbn:
            messagebox.showerror("Error", "ISBN required.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE book SET {', '.join(updates)} WHERE isbn13=%s OR isbn10=%s",
                values + [isbn, isbn]
            )
            conn.commit()
            messagebox.showinfo("Success", "Book details updated.")
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            cursor.close()
            conn.close()

    # UNIVERSITY / DEPARTMENT / COURSE
    
    def _build_university_section(self):
        tk.Label(self.content, text="University & Courses", font=("Helvetica", 16, "bold")).pack(pady=10)

        self.uni_name = tk.Entry(self.content, width=40)
        self.addr_id = tk.Entry(self.content, width=40)
        self.rep_fn = tk.Entry(self.content, width=40)
        self.rep_ln = tk.Entry(self.content, width=40)
        self.rep_email = tk.Entry(self.content, width=40)
        self.rep_phone = tk.Entry(self.content, width=40)

        for lbl, widget in [
            ("University Name*", self.uni_name),
            ("Address ID*", self.addr_id),
            ("Rep First Name", self.rep_fn),
            ("Rep Last Name", self.rep_ln),
            ("Rep Email", self.rep_email),
            ("Rep Phone", self.rep_phone)
        ]:
            tk.Label(self.content, text=lbl).pack()
            widget.pack()

        tk.Button(self.content, text="Create University", command=self.create_university).pack(pady=5)

        # Department
        tk.Label(self.content, text="Department").pack(pady=6)
        self.dept_uni_id = tk.Entry(self.content, width=40)
        self.dept_name = tk.Entry(self.content, width=40)

        tk.Label(self.content, text="University ID*").pack()
        self.dept_uni_id.pack()
        tk.Label(self.content, text="Department Name*").pack()
        self.dept_name.pack()
        tk.Button(self.content, text="Add Department", command=self.add_department).pack(pady=4)

        # Course
        tk.Label(self.content, text="Course").pack(pady=6)
        self.course_dept_id = tk.Entry(self.content, width=40)
        self.course_code = tk.Entry(self.content, width=40)
        self.course_name = tk.Entry(self.content, width=40)

        tk.Label(self.content, text="Department ID*").pack()
        self.course_dept_id.pack()
        tk.Label(self.content, text="Course Code*").pack()
        self.course_code.pack()
        tk.Label(self.content, text="Course Name*").pack()
        self.course_name.pack()
        tk.Button(self.content, text="Add Course", command=self.add_course).pack(pady=4)

    def create_university(self):
        if not self.uni_name.get().strip():
            messagebox.showerror("Error", "University name is required.")
            return
        if not self.addr_id.get().strip():
            messagebox.showerror("Error", "Address ID is required.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO university
                (university_name, address_id, rep_first_name, rep_last_name, rep_email, rep_phone)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (
                self.uni_name.get().strip(),
                int(self.addr_id.get().strip()),
                self.rep_fn.get().strip() or None,
                self.rep_ln.get().strip() or None,
                self.rep_email.get().strip() or None,
                self.rep_phone.get().strip() or None
            ))

            conn.commit()
            messagebox.showinfo("Success", "University added.")
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            cursor.close()
            conn.close()

    def add_department(self):
        if not self.dept_uni_id.get().strip():
            messagebox.showerror("Error", "University ID is required.")
            return
        if not self.dept_name.get().strip():
            messagebox.showerror("Error", "Department name is required.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO department (university_id, department_name) VALUES (%s,%s)",
                (int(self.dept_uni_id.get()), self.dept_name.get().strip())
            )

            conn.commit()
            messagebox.showinfo("Success", "Department added.")
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            cursor.close()
            conn.close()

    def add_course(self):
        if not self.course_dept_id.get().strip():
            messagebox.showerror("Error", "Department ID is required.")
            return
        if not self.course_code.get().strip():
            messagebox.showerror("Error", "Course code is required.")
            return
        if not self.course_name.get().strip():
            messagebox.showerror("Error", "Course name is required.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO course (department_id, course_code, course_name)
                VALUES (%s,%s,%s)
            """, (
                int(self.course_dept_id.get()),
                self.course_code.get().strip(),
                self.course_name.get().strip()
            ))

            conn.commit()
            messagebox.showinfo("Success", "Course added.")
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            cursor.close()
            conn.close()

    # TICKETS
    def _build_ticket_section(self):
        tk.Label(self.content, text="Ticket Management", font=("Helvetica", 16, "bold")).pack(pady=10)

        self.ticket_id = tk.Entry(self.content, width=30)
        self.ticket_status = tk.Entry(self.content, width=30)
        self.employee_id = tk.Entry(self.content, width=30)
        self.ticket_solution = tk.Entry(self.content, width=50)  # Added solution field

        tk.Label(self.content, text="Ticket ID*").pack()
        self.ticket_id.pack()
        tk.Label(self.content, text="New Status (Open / In Progress / Resolved)*").pack()
        self.ticket_status.pack()
        tk.Label(self.content, text="Employee ID*").pack()
        self.employee_id.pack()
        tk.Label(self.content, text="Solution (Optional, if resolving)").pack()
        self.ticket_solution.pack()

        tk.Button(self.content, text="Update Ticket", command=self.update_ticket).pack(pady=8)

    def update_ticket(self):
        status = self.ticket_status.get().strip()
        solution = self.ticket_solution.get().strip()
        if status not in ("Open", "In Progress", "Resolved"):
            messagebox.showerror("Error", "Invalid ticket status.")
            return

        if not self.employee_id.get().strip():
            messagebox.showerror("Error", "Employee ID is required.")
            return

        try:
            ticket_id = int(self.ticket_id.get())
            employee_id = int(self.employee_id.get())
        except ValueError:
            messagebox.showerror("Error", "Ticket ID and Employee ID must be integers.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT ticket_status FROM ticket WHERE ticket_id=%s",
                (ticket_id,)
            )
            res = cursor.fetchone()
            if not res:
                messagebox.showerror("Error", "Ticket not found.")
                return

            old_status = res[0]

            # Update ticket with solution and date_completed if resolved
            if status == "Resolved":
                cursor.execute("""
                    UPDATE ticket
                    SET ticket_status=%s, resolved_by_admin=%s, solution=%s, date_completed=CURRENT_TIMESTAMP
                    WHERE ticket_id=%s
                """, (status, employee_id, solution, ticket_id))
            else:
                cursor.execute("""
                    UPDATE ticket
                    SET ticket_status=%s, resolved_by_admin=%s, solution=%s
                    WHERE ticket_id=%s
                """, (status, employee_id, solution, ticket_id))

            # Insert into ticket_state_history
            cursor.execute("""
                INSERT INTO ticket_state_history
                (ticket_id, employee_id, old_status, new_status)
                VALUES (%s,%s,%s,%s)
            """, (ticket_id, employee_id, old_status, status))

            conn.commit()
            messagebox.showinfo("Success", "Ticket updated.")
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            cursor.close()
            conn.close()

    # COURSE–BOOK ASSOCIATION
    def _build_course_book_section(self):
        tk.Label(self.content, text="Course–Book Association", font=("Helvetica", 16, "bold")).pack(pady=10)

        tk.Label(self.content, text="Course ID*").pack()
        self.cb_course_id = tk.Entry(self.content, width=40)
        self.cb_course_id.pack()

        tk.Label(self.content, text="Book ID*").pack()
        self.cb_book_id = tk.Entry(self.content, width=40)
        self.cb_book_id.pack()

        tk.Label(self.content, text="Usage Type* (Required / Recommended)").pack()
        self.cb_usage_type_var = tk.StringVar()
        self.cb_usage_type = tk.OptionMenu(self.content, self.cb_usage_type_var, "Required", "Recommended")
        self.cb_usage_type.pack()

        tk.Button(self.content, text="Create Course–Book Link", command=self.create_course_book).pack(pady=12)

    def create_course_book(self):
        course_id = self.cb_course_id.get().strip()
        book_id = self.cb_book_id.get().strip()
        usage_type = self.cb_usage_type_var.get().strip()

        if not course_id or not book_id or not usage_type:
            messagebox.showerror("Error", "Course ID, Book ID, and Usage Type are required.")
            return

        if usage_type not in ["Required", "Recommended"]:
            messagebox.showerror("Error", "Usage Type must be either 'Required' or 'Recommended'.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO course_book (course_id, book_id, usage_type)
                VALUES (%s, %s, %s)
                """,
                (int(course_id), int(book_id), usage_type)
            )

            conn.commit()
            messagebox.showinfo("Success", "Book successfully associated with course.")

        except Error as e:
            messagebox.showerror("Database Error", f"Could not create association:\n{e}")

        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
