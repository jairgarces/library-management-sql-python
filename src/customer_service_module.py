import tkinter as tk
from tkinter import messagebox, ttk
from mysql.connector import Error
from db import get_connection
from datetime import datetime

class CustomerServiceModule(tk.Toplevel):
    def __init__(self, master=None, cs_employee_id=None):
        super().__init__(master)
        self.title("Customer Service Module")
        self.geometry("700x700")
        self.cs_employee_id = cs_employee_id  # Logged-in CS employee ID

        # ===== Scrollable Canvas Setup =====
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

        tk.Label(self.content, text="Customer Service Actions", font=("Helvetica", 16, "bold")).pack(pady=10)

        self._build_create_ticket_section()
        self._build_update_ticket_section()
        self._build_update_order_section()

    # CREATE TROUBLE TICKET
    def _build_create_ticket_section(self):
        tk.Label(self.content, text="Create Trouble Ticket", font=("Helvetica", 14, "bold")).pack(pady=8)

        # Category ID (integer input)
        tk.Label(self.content, text="Category ID*").pack()
        self.ticket_category = tk.Entry(self.content, width=20)
        self.ticket_category.pack()

        # Title
        tk.Label(self.content, text="Title*").pack()
        self.ticket_title = tk.Entry(self.content, width=50)
        self.ticket_title.pack()

        # Description
        tk.Label(self.content, text="Description*").pack()
        self.ticket_description = tk.Text(self.content, width=50, height=5)
        self.ticket_description.pack()

        tk.Button(self.content, text="Submit Ticket", command=self.create_ticket).pack(pady=5)

    def create_ticket(self):
        category_id = self.ticket_category.get().strip()
        title = self.ticket_title.get().strip()
        description = self.ticket_description.get("1.0", tk.END).strip()

        if not category_id or not title or not description:
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            category_id = int(category_id)
        except ValueError:
            messagebox.showerror("Error", "Category ID must be an integer.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ticket (category_id, created_by_cs, title, ticket_description, ticket_status)
                VALUES (%s,%s,%s,%s,'Open')
            """, (category_id, self.cs_employee_id, title, description))
            conn.commit()
            messagebox.showinfo("Success", "Trouble ticket created with status 'Open'.")
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            cursor.close()
            conn.close()

    # UPDATE TROUBLE TICKET
    def _build_update_ticket_section(self):
        tk.Label(self.content, text="Update Trouble Ticket", font=("Helvetica", 14, "bold")).pack(pady=8)

        tk.Label(self.content, text="Ticket ID*").pack()
        self.update_ticket_id = tk.Entry(self.content, width=20)
        self.update_ticket_id.pack()

        tk.Label(self.content, text="Assign to Admin (Optional)").pack()
        self.update_ticket_admin = tk.Entry(self.content, width=20)
        self.update_ticket_admin.pack()

        tk.Label(self.content, text="Description Update").pack()
        self.update_ticket_description = tk.Text(self.content, width=50, height=5)
        self.update_ticket_description.pack()

        tk.Button(self.content, text="Update Ticket", command=self.update_ticket).pack(pady=5)

    def update_ticket(self):
        ticket_id = self.update_ticket_id.get().strip()
        admin_id = self.update_ticket_admin.get().strip()
        description = self.update_ticket_description.get("1.0", tk.END).strip()

        if not ticket_id:
            messagebox.showerror("Error", "Ticket ID is required.")
            return

        try:
            ticket_id = int(ticket_id)
        except ValueError:
            messagebox.showerror("Error", "Ticket ID must be an integer.")
            return

        if admin_id:
            try:
                admin_id = int(admin_id)
            except ValueError:
                messagebox.showerror("Error", "Admin ID must be an integer.")
                return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Check current ticket status
            cursor.execute("SELECT ticket_status FROM ticket WHERE ticket_id=%s", (ticket_id,))
            res = cursor.fetchone()
            if not res:
                messagebox.showerror("Error", "Ticket not found.")
                return
            old_status = res[0]

            if old_status != "Open":
                messagebox.showerror("Error", "Only tickets with status 'Open' can be updated by CS.")
                return

            # Update fields
            update_fields = []
            params = []

            new_status = old_status

            if admin_id:
                update_fields.append("resolved_by_admin=%s")
                params.append(admin_id)
                update_fields.append("ticket_status=%s")
                new_status = "In Progress"
                params.append(new_status)
            if description:
                update_fields.append("ticket_description=%s")
                params.append(description)

            if update_fields:
                cursor.execute(f"UPDATE ticket SET {', '.join(update_fields)} WHERE ticket_id=%s", (*params, ticket_id))
                # Insert into ticket_state_history
                cursor.execute("""
                    INSERT INTO ticket_state_history (ticket_id, employee_id, old_status, new_status)
                    VALUES (%s,%s,%s,%s)
                """, (ticket_id, self.cs_employee_id, old_status, new_status))
                conn.commit()
                messagebox.showinfo("Success", f"Ticket updated to status '{new_status}'.")
            else:
                messagebox.showinfo("Info", "No changes provided.")
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            cursor.close()
            conn.close()

    # UPDATE ORDER STATUS
    def _build_update_order_section(self):
        tk.Label(self.content, text="Update Order Status", font=("Helvetica", 14, "bold")).pack(pady=8)

        tk.Label(self.content, text="Order ID*").pack()
        self.order_id_entry = tk.Entry(self.content, width=20)
        self.order_id_entry.pack()

        tk.Label(self.content, text="New Status*").pack()
        self.order_status_combobox = ttk.Combobox(self.content, width=20)
        self.order_status_combobox['values'] = ["Cancelled", "Completed", "Shipped", "Pending", "Paid"]
        self.order_status_combobox.pack()

        tk.Button(self.content, text="Update Order", command=self.update_order).pack(pady=5)

    def update_order(self):
        order_id = self.order_id_entry.get().strip()
        new_status = self.order_status_combobox.get()

        if not order_id or not new_status:
            messagebox.showerror("Error", "Order ID and New Status are required.")
            return

        try:
            order_id = int(order_id)
        except ValueError:
            messagebox.showerror("Error", "Order ID must be an integer.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT order_status FROM customer_order WHERE order_id=%s", (order_id,))
            res = cursor.fetchone()
            if not res:
                messagebox.showerror("Error", "Order not found.")
                return

            old_status = res[0]
            if new_status == "Cancelled" and old_status not in ("Pending", "Paid"):
                messagebox.showerror("Error", "Order cannot be cancelled at this stage.")
                return

            cursor.execute("UPDATE customer_order SET order_status=%s WHERE order_id=%s", (new_status, order_id))
            conn.commit()
            messagebox.showinfo("Success", f"Order status updated from {old_status} to {new_status}.")
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            cursor.close()
            conn.close()
