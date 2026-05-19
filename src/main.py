import tkinter as tk
from tkinter import messagebox
from mysql.connector import Error

from db import get_connection
from student_module import StudentModule
from reports_module import ReportsModule
from admin_module import AdminModule
from super_admin_module import SuperAdminModule
from customer_service_module import CustomerServiceModule  


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Book Fetch System")
        self.geometry("400x400")  

        # title
        title_label = tk.Label(
            self,
            text="Book Fetch Management Console",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(pady=15)

        # db status
        self.db_status_label = tk.Label(self, text="Checking database connection...", fg="gray")
        self.db_status_label.pack(pady=5)

        self.check_db_connection()

        # main menu
        menu_frame = tk.Frame(self)
        menu_frame.pack(pady=20)

        student_btn = tk.Button(
            menu_frame,
            text="Student Module",
            width=25,
            command=self.open_student_module
        )
        student_btn.pack(pady=5)

        super_admin_btn = tk.Button(
            menu_frame,
            text="Super Admin Module",
            width=25,
            command=self.open_super_admin_module
        )
        super_admin_btn.pack(pady=5)


        admin_btn = tk.Button(
            menu_frame,
            text="Administrator Module",
            width=25,
            command=self.open_admin_module
        )
        admin_btn.pack(pady=5)


        cs_btn = tk.Button(
            menu_frame,
            text="Customer Service Module",
            width=25,
            command=self.open_cs_module
        )
        cs_btn.pack(pady=5)

        reports_btn = tk.Button(
            menu_frame,
            text="Reports",
            width=25,
            command=self.open_reports_module
        )
        reports_btn.pack(pady=5)

        exit_btn = tk.Button(
            menu_frame,
            text="Exit",
            width=25,
            command=self.destroy
        )
        exit_btn.pack(pady=5)

        # Footer / credits
        footer_label = tk.Label(
            self,
            text="CISC 450 – Book Fetch Project",
            font=("Helvetica", 9),
            fg="gray"
        )
        footer_label.pack(side="bottom", pady=10)

    def check_db_connection(self):
        """
        Try a simple query to confirm the DB connection works.
        Update the status label accordingly.
        """
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            self.db_status_label.config(text="Database connection: OK", fg="green")
        except Error as e:
            self.db_status_label.config(text="Database connection: FAILED", fg="red")
            messagebox.showerror("Database Error", f"Could not connect to DB:\n{e}")

    
    # Module Open Methods
    
    def open_student_module(self):
        """Open the StudentModule window."""
        StudentModule(self)

    def open_admin_module(self):
        """Open the AdminModule window."""
        AdminModule(self)

    def open_super_admin_module(self):
        """Open the SuperAdminModule window."""
        # Replace 3 with actual super_admin_id after full data insert but should be fine
        SuperAdminModule(self, super_admin_id=3)

    def open_cs_module(self):
        """Open the CustomerServiceModule window."""
        # Replace 2 with actual CS employee ID after we fully insert data
        CustomerServiceModule(self, cs_employee_id=1)

    def open_reports_module(self):
        """Open the ReportsModule window."""
        ReportsModule(self)


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
