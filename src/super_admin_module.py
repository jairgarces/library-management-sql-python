import tkinter as tk
from tkinter import messagebox
from mysql.connector import Error
from db import get_connection
from datetime import datetime

class SuperAdminModule(tk.Toplevel):
    def __init__(self, master=None, super_admin_id=None):
        super().__init__(master)
        self.title("Super Administrator Module")
        self.geometry("650x700")
        self.super_admin_id = super_admin_id  # ID of logged-in super admin

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

        # ===== Title =====
        tk.Label(self.content, text="Super Admin Actions", font=("Helvetica", 16, "bold")).pack(pady=10)

        # ===== Build sections =====
        self._build_create_employee_section()
        self._build_create_admin_section()
        self._build_deactivate_section()

    # CREATE CUSTOMER SERVICE EMPLOYEE
    def _build_create_employee_section(self):
        tk.Label(self.content, text="Create Customer Service Employee", font=("Helvetica", 14, "bold")).pack(pady=8)

        self.cs_first_name = tk.Entry(self.content, width=40)
        self.cs_last_name = tk.Entry(self.content, width=40)
        self.cs_email = tk.Entry(self.content, width=40)
        self.cs_phone = tk.Entry(self.content, width=40)
        self.cs_address_id = tk.Entry(self.content, width=40)
        self.cs_gender = tk.Entry(self.content, width=40)
        self.cs_salary = tk.Entry(self.content, width=40)
        self.cs_ssn = tk.Entry(self.content, width=40)

        for lbl, widget in [
            ("First Name*", self.cs_first_name),
            ("Last Name*", self.cs_last_name),
            ("Email*", self.cs_email),
            ("Phone", self.cs_phone),
            ("Address ID*", self.cs_address_id),
            ("Gender", self.cs_gender),
            ("Salary", self.cs_salary),
            ("SSN", self.cs_ssn)
        ]:
            tk.Label(self.content, text=lbl).pack()
            widget.pack()

        tk.Button(self.content, text="Create CS Employee", command=self.create_cs_employee).pack(pady=5)

    def create_cs_employee(self):
        first = self.cs_first_name.get().strip()
        last = self.cs_last_name.get().strip()
        email = self.cs_email.get().strip()
        phone = self.cs_phone.get().strip() or None
        address_id = self.cs_address_id.get().strip()
        gender = self.cs_gender.get().strip() or None
        salary = self.cs_salary.get().strip() or None
        ssn = self.cs_ssn.get().strip() or None

        if not first or not last or not email or not address_id:
            messagebox.showerror("Error", "First Name, Last Name, Email, and Address ID are required.")
            return

        try:
            salary_val = float(salary) if salary else None
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO employee
                (address_id, first_name, last_name, gender, salary, ssn, employee_email, phone, employee_role)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'customer_support')
            """, (int(address_id), first, last, gender, salary_val, ssn, email, phone))

            conn.commit()
            messagebox.showinfo("Success", "Customer Service Employee created.")

            cursor.execute("""
                INSERT INTO account_audit (target_employee, performed_by, action_type, note)
                VALUES (%s,%s,'create','Created by super admin')
            """, (cursor.lastrowid, self.super_admin_id))
            conn.commit()

        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            cursor.close()
            conn.close()

    # CREATE ADMIN

    def _build_create_admin_section(self):
        tk.Label(self.content, text="Create Admin", font=("Helvetica", 14, "bold")).pack(pady=8)

        self.admin_first_name = tk.Entry(self.content, width=40)
        self.admin_last_name = tk.Entry(self.content, width=40)
        self.admin_email = tk.Entry(self.content, width=40)
        self.admin_phone = tk.Entry(self.content, width=40)
        self.admin_address_id = tk.Entry(self.content, width=40)
        self.admin_gender = tk.Entry(self.content, width=40)
        self.admin_salary = tk.Entry(self.content, width=40)
        self.admin_ssn = tk.Entry(self.content, width=40)

        for lbl, widget in [
            ("First Name*", self.admin_first_name),
            ("Last Name*", self.admin_last_name),
            ("Email*", self.admin_email),
            ("Phone", self.admin_phone),
            ("Address ID*", self.admin_address_id),
            ("Gender", self.admin_gender),
            ("Salary", self.admin_salary),
            ("SSN", self.admin_ssn)
        ]:
            tk.Label(self.content, text=lbl).pack()
            widget.pack()

        tk.Button(self.content, text="Create Admin", command=self.create_admin).pack(pady=5)

    def create_admin(self):
        first = self.admin_first_name.get().strip()
        last = self.admin_last_name.get().strip()
        email = self.admin_email.get().strip()
        phone = self.admin_phone.get().strip() or None
        address_id = self.admin_address_id.get().strip()
        gender = self.admin_gender.get().strip() or None
        salary = self.admin_salary.get().strip() or None
        ssn = self.admin_ssn.get().strip() or None

        if not first or not last or not email or not address_id:
            messagebox.showerror("Error", "First Name, Last Name, Email, and Address ID are required.")
            return

        try:
            salary_val = float(salary) if salary else None
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO employee
                (address_id, first_name, last_name, gender, salary, ssn, employee_email, phone, employee_role)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'admin')
            """, (int(address_id), first, last, gender, salary_val, ssn, email, phone))

            conn.commit()
            messagebox.showinfo("Success", "Admin created.")

            cursor.execute("""
                INSERT INTO account_audit (target_employee, performed_by, action_type, note)
                VALUES (%s,%s,'create','Created by super admin')
            """, (cursor.lastrowid, self.super_admin_id))
            conn.commit()

        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            cursor.close()
            conn.close()

    # DEACTIVATE/REACTIVATE EMPLOYEE
    def _build_deactivate_section(self):
        tk.Label(self.content, text="Deactivate / Reactivate Employee", font=("Helvetica", 14, "bold")).pack(pady=10)

        self.deact_employee_id = tk.Entry(self.content, width=40)
        tk.Label(self.content, text="Employee ID*").pack()
        self.deact_employee_id.pack()

        self.deact_var = tk.StringVar()
        self.deact_var.set("Deactivate")
        tk.OptionMenu(self.content, self.deact_var, "Deactivate", "Reactivate").pack(pady=5)

        tk.Button(self.content, text="Update Status", command=self.deactivate_employee).pack(pady=5)

    def deactivate_employee(self):
        emp_id = self.deact_employee_id.get().strip()
        action = self.deact_var.get()

        if not emp_id:
            messagebox.showerror("Error", "Employee ID required.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT employee_role FROM employee WHERE employee_id=%s", (int(emp_id),))
            res = cursor.fetchone()
            if not res:
                messagebox.showerror("Error", "Employee not found.")
                return
            role = res[0]

            if action == "Deactivate":
                if role == "admin":
                    cursor.execute("""
                        UPDATE ticket
                        SET resolved_by_admin = NULL,
                            ticket_status = 'New'
                        WHERE resolved_by_admin=%s
                    """, (int(emp_id),))
                cursor.execute("""
                    INSERT INTO account_audit (target_employee, performed_by, action_type, note)
                    VALUES (%s,%s,'deactivate','Deactivated by super admin')
                """, (int(emp_id), self.super_admin_id))
            else:
                cursor.execute("""
                    INSERT INTO account_audit (target_employee, performed_by, action_type, note)
                    VALUES (%s,%s,'reactivate','Reactivated by super admin')
                """, (int(emp_id), self.super_admin_id))

            conn.commit()
            messagebox.showinfo("Success", f"Employee {action}d successfully.")
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            cursor.close()
            conn.close()
