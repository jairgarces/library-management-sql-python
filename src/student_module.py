import tkinter as tk
from tkinter import messagebox
from db import get_connection
from mysql.connector import Error
import re
import platform


class StudentModule(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Student Module")
        self.geometry("550x700")  # Window size; content will scroll

        # Detect macOS for scroll behavior
        self._is_macos = (platform.system() == "Darwin")

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        # Canvas stored on self so handlers can access it
        self.canvas = tk.Canvas(container)
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Frame inside the canvas where all widgets go
        self.content_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")

        # Update scrollregion whenever content changes
        def on_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.content_frame.bind("<Configure>", on_configure)

        # Enable mouse wheel / trackpad scrolling
        self._bind_mousewheel()

        self.entries = {}

        self.cart_student_id_entry = None
        self.cart_id_entry = None
        self.book_id_entry = None
        self.quantity_entry = None

        self.order_cart_id_entry = None
        self.shipping_type_entry = None
        self.card_name_entry = None
        self.card_number_entry = None
        self.card_type_entry = None
        self.card_exp_entry = None

        # Update cart section entries
        self.update_cart_id_entry = None
        self.update_book_id_entry = None
        self.update_quantity_entry = None

        # Cancel order section entries
        self.cancel_order_id_entry = None
        self.cancel_student_id_entry = None

        # Review section entries
        self.review_student_id_entry = None
        self.review_book_id_entry = None
        self.review_rating_entry = None

        self._build_form(self.content_frame)
        self._build_cart_section(self.content_frame)
        self._build_add_book_section(self.content_frame)
        self._build_place_order_section(self.content_frame)
        self._build_update_cart_section(self.content_frame)
        self._build_cancel_order_section(self.content_frame)
        self._build_review_section(self.content_frame)

    def _on_mousewheel(self, event):
        """
        Mouse wheel / trackpad scrolling.

        - On Windows: event.delta is typically +/-120 -> scale it down.
        - On macOS: event.delta is usually small (+/-1 or +/-2) -> don't divide.
        """
        if self._is_macos:
            # macOS: use delta directly (and maybe scale a bit)
            step = -1 * event.delta
            # clamp so it doesn't go crazy if delta is large
            if step > 0:
                step = min(step, 5)
            else:
                step = max(step, -5)
            self.canvas.yview_scroll(step, "units")
        else:
            # Windows / others: normalize by 120
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_linux(self, event):
        """Scroll handler for Linux (Button-4 / Button-5)."""
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

    def _bind_mousewheel(self):
        """Bind mousewheel events to the whole window."""
        # Windows / macOS
        self.bind_all("<MouseWheel>", self._on_mousewheel)
        # Linux
        self.bind_all("<Button-4>", self._on_mousewheel_linux)
        self.bind_all("<Button-5>", self._on_mousewheel_linux)

    def _validate_int(self, value_if_allowed: str) -> bool:
        """
        Allow only empty string or digits.
        Used for Entry validatecommand.
        """
        return value_if_allowed == "" or value_if_allowed.isdigit()

    def _make_int_entry(self, parent, width=20) -> tk.Entry:
        """
        Create an Entry widget that only allows integer input.
        """
        vcmd = (parent.register(self._validate_int), "%P")
        entry = tk.Entry(parent, width=width, validate="key", validatecommand=vcmd)
        return entry

    def _valid_date(self, date_str: str) -> bool:
        """
        Validate date in YYYY-MM-DD format (very basic).
        """
        if not date_str:
            return True  # allow empty, caller handles required or not
        pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        return bool(pattern.match(date_str))

    # Create Student
    def _build_form(self, parent):
        title = tk.Label(parent, text="Create New Student", font=("Helvetica", 16, "bold"))
        title.pack(pady=10)

        form_frame = tk.Frame(parent)
        form_frame.pack(pady=10)

        # (label text, field key, is_int_field)
        form_fields = [
            ("Username", "username", False),                      # REQUIRED, UNIQUE
            ("First Name", "first_name", False),                 # REQUIRED
            ("Last Name", "last_name", False),                   # REQUIRED
            ("Email", "email", False),                           # REQUIRED, UNIQUE
            ("Phone", "phone", False),                           # optional
            ("Birth Date (YYYY-MM-DD)", "birth_date", False),    # optional, date format check
            ("Major", "major", False),                           # optional
            ("Student Year (e.g., Freshman)", "Student_year", False),  # optional
            ("Student Status", "student_status", False),         # optional
            ("University ID", "university_id", True),            # REQUIRED (FK, INT)
            ("Address ID", "address_id", True),                  # REQUIRED (FK, INT)
        ]

        for label_text, field_name, is_int in form_fields:
            row = tk.Frame(form_frame)
            row.pack(fill="x", pady=4)

            label = tk.Label(row, text=label_text, width=24, anchor="w")
            label.pack(side="left")

            if is_int:
                entry = self._make_int_entry(row, width=30)
            else:
                entry = tk.Entry(row, width=30)
            entry.pack(side="left")

            self.entries[field_name] = entry

        submit_btn = tk.Button(parent, text="Save Student", command=self.save_student)
        submit_btn.pack(pady=10)

    def save_student(self):
        data = {field: entry.get().strip() for field, entry in self.entries.items()}

        required_fields = ["username", "first_name", "last_name", "email",
                           "university_id", "address_id"]
        missing = [f for f in required_fields if not data[f]]

        if missing:
            messagebox.showerror(
                "Error",
                "The following fields are required:\n- " + "\n- ".join(missing)
            )
            return

        # Validate birth_date format if provided
        if data["birth_date"] and not self._valid_date(data["birth_date"]):
            messagebox.showerror(
                "Error",
                "Birth Date must be in YYYY-MM-DD format."
            )
            return

        try:
            data["university_id"] = int(data["university_id"])
            data["address_id"] = int(data["address_id"])
        except ValueError:
            messagebox.showerror(
                "Error",
                "University ID and Address ID must be integers."
            )
            return

        for optional in ["phone", "birth_date", "major", "Student_year", "student_status"]:
            if data[optional] == "":
                data[optional] = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            sql = """
                INSERT INTO student
                (username, university_id, Student_year, student_status,
                 phone, major, last_name, first_name, email, birth_date, address_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(sql, (
                data["username"],
                data["university_id"],
                data["Student_year"],
                data["student_status"],
                data["phone"],
                data["major"],
                data["last_name"],
                data["first_name"],
                data["email"],
                data["birth_date"],
                data["address_id"],
            ))

            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Success", "Student created successfully!")

            for entry in self.entries.values():
                entry.delete(0, tk.END)

        except Error as e:
            messagebox.showerror("Database Error", str(e))

    # Create Cart for a Student
    def _build_cart_section(self, parent):
        separator = tk.Label(parent, text="────────────────────────────────────────")
        separator.pack(pady=10)

        title = tk.Label(parent, text="Create Cart for Existing Student",
                         font=("Helvetica", 14, "bold"))
        title.pack(pady=5)

        desc = tk.Label(
            parent,
            text="Enter an existing student_id to create an Active cart.\n"
                 "Each student can only have one cart.",
            justify="center"
        )
        desc.pack(pady=5)

        row = tk.Frame(parent)
        row.pack(pady=5)

        label = tk.Label(row, text="Student ID", width=24, anchor="w")
        label.pack(side="left")

        self.cart_student_id_entry = self._make_int_entry(row, width=30)
        self.cart_student_id_entry.pack(side="left")

        btn = tk.Button(parent, text="Create Cart", command=self.create_cart_for_student)
        btn.pack(pady=10)

    def create_cart_for_student(self):
        student_id_str = self.cart_student_id_entry.get().strip()

        if not student_id_str:
            messagebox.showerror("Error", "Student ID is required.")
            return

        try:
            student_id = int(student_id_str)
        except ValueError:
            messagebox.showerror("Error", "Student ID must be an integer.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT student_id FROM student WHERE student_id = %s", (student_id,))
            row = cursor.fetchone()
            if not row:
                cursor.close()
                conn.close()
                messagebox.showerror("Error", f"No student found with ID {student_id}.")
                return

            cursor.execute(
                "SELECT cart_id, cart_status FROM cart WHERE student_id = %s",
                (student_id,)
            )
            existing = cursor.fetchone()
            if existing:
                cart_id, status = existing
                cursor.close()
                conn.close()
                messagebox.showwarning(
                    "Cart Exists",
                    f"Student {student_id} already has a cart (ID {cart_id}) "
                    f"with status '{status}'."
                )
                return

            cursor.execute(
                "INSERT INTO cart (student_id, cart_status) VALUES (%s, 'Active')",
                (student_id,)
            )
            conn.commit()

            cart_id = cursor.lastrowid

            cursor.close()
            conn.close()

            messagebox.showinfo(
                "Success",
                f"Cart created successfully for student {student_id}.\n"
                f"New cart ID: {cart_id}"
            )

            self.cart_student_id_entry.delete(0, tk.END)

        except Error as e:
            messagebox.showerror("Database Error", str(e))

    # Add Book to Cart
    def _build_add_book_section(self, parent):
        separator = tk.Label(parent, text="────────────────────────────────────────")
        separator.pack(pady=10)

        title = tk.Label(
            parent,
            text="Add Book to Cart",
            font=("Helvetica", 14, "bold")
        )
        title.pack(pady=5)

        frame = tk.Frame(parent)
        frame.pack(pady=10)

        cart_row = tk.Frame(frame)
        cart_row.pack(fill="x", pady=4)
        tk.Label(cart_row, text="Cart ID", width=12, anchor="w").pack(side="left")
        self.cart_id_entry = self._make_int_entry(cart_row, width=20)
        self.cart_id_entry.pack(side="left")

        book_row = tk.Frame(frame)
        book_row.pack(fill="x", pady=4)
        tk.Label(book_row, text="Book ID", width=12, anchor="w").pack(side="left")
        self.book_id_entry = self._make_int_entry(book_row, width=20)
        self.book_id_entry.pack(side="left")

        qty_row = tk.Frame(frame)
        qty_row.pack(fill="x", pady=4)
        tk.Label(qty_row, text="Quantity", width=12, anchor="w").pack(side="left")
        self.quantity_entry = self._make_int_entry(qty_row, width=20)
        self.quantity_entry.pack(side="left")

        add_btn = tk.Button(parent, text="Add to Cart", command=self.add_book_to_cart)
        add_btn.pack(pady=10)

    def add_book_to_cart(self):
        cart_id = self.cart_id_entry.get().strip()
        book_id = self.book_id_entry.get().strip()
        qty_str = self.quantity_entry.get().strip()

        if not cart_id or not book_id or not qty_str:
            messagebox.showerror("Error", "Cart ID, Book ID, and Quantity are required.")
            return

        try:
            cart_id = int(cart_id)
            book_id = int(book_id)
            quantity = int(qty_str)
        except ValueError:
            messagebox.showerror("Error", "IDs and quantity must be integers.")
            return

        if quantity <= 0:
            messagebox.showerror("Error", "Quantity must be greater than zero.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT cart_id FROM cart WHERE cart_id = %s", (cart_id,))
            if not cursor.fetchone():
                messagebox.showerror("Error", f"No cart found with ID {cart_id}.")
                conn.close()
                return

            cursor.execute(
                "SELECT price, quantity FROM book WHERE book_id = %s",
                (book_id,)
            )
            row = cursor.fetchone()
            if not row:
                messagebox.showerror("Error", f"No book found with ID {book_id}.")
                conn.close()
                return

            price, inventory_qty = row

            if quantity > inventory_qty:
                messagebox.showerror(
                    "Error",
                    f"Only {inventory_qty} units available for book {book_id}."
                )
                conn.close()
                return

            cursor.execute(
                """
                INSERT INTO cart_item (cart_id, book_id, quantity, unit_price)
                VALUES (%s, %s, %s, %s)
                """,
                (cart_id, book_id, quantity, price)
            )

            cursor.execute(
                """
                UPDATE book
                SET quantity = quantity - %s
                WHERE book_id = %s
                """,
                (quantity, book_id)
            )

            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo(
                "Success",
                f"Added {quantity} of Book {book_id} to Cart {cart_id}."
            )

            self.cart_id_entry.delete(0, tk.END)
            self.book_id_entry.delete(0, tk.END)
            self.quantity_entry.delete(0, tk.END)

        except Error as e:
            messagebox.showerror("Database Error", str(e))

    # Place Order from Cart
    def _build_place_order_section(self, parent):
        separator = tk.Label(parent, text="────────────────────────────────────────")
        separator.pack(pady=10)

        title = tk.Label(
            parent,
            text="Place Order from Cart",
            font=("Helvetica", 14, "bold")
        )
        title.pack(pady=5)

        frame = tk.Frame(parent)
        frame.pack(pady=10)

        row_cart = tk.Frame(frame)
        row_cart.pack(fill="x", pady=4)
        tk.Label(row_cart, text="Cart ID", width=16, anchor="w").pack(side="left")
        self.order_cart_id_entry = self._make_int_entry(row_cart, width=25)
        self.order_cart_id_entry.pack(side="left")

        row_ship = tk.Frame(frame)
        row_ship.pack(fill="x", pady=4)
        tk.Label(row_ship, text="Shipping Type", width=16, anchor="w").pack(side="left")
        self.shipping_type_entry = tk.Entry(row_ship, width=25)
        self.shipping_type_entry.insert(0, "Standard")
        self.shipping_type_entry.pack(side="left")

        row_name = tk.Frame(frame)
        row_name.pack(fill="x", pady=4)
        tk.Label(row_name, text="Card Name", width=16, anchor="w").pack(side="left")
        self.card_name_entry = tk.Entry(row_name, width=25)
        self.card_name_entry.pack(side="left")

        row_num = tk.Frame(frame)
        row_num.pack(fill="x", pady=4)
        tk.Label(row_num, text="Card Number", width=16, anchor="w").pack(side="left")
        self.card_number_entry = tk.Entry(row_num, width=25)
        self.card_number_entry.pack(side="left")

        row_type = tk.Frame(frame)
        row_type.pack(fill="x", pady=4)
        tk.Label(row_type, text="Card Type", width=16, anchor="w").pack(side="left")
        self.card_type_entry = tk.Entry(row_type, width=25)
        self.card_type_entry.insert(0, "Visa")
        self.card_type_entry.pack(side="left")

        row_exp = tk.Frame(frame)
        row_exp.pack(fill="x", pady=4)
        tk.Label(row_exp, text="Card Exp (YYYY-MM-DD)", width=20, anchor="w").pack(side="left")
        self.card_exp_entry = tk.Entry(row_exp, width=21)
        self.card_exp_entry.pack(side="left")

        place_btn = tk.Button(parent, text="Place Order", command=self.place_order_from_cart)
        place_btn.pack(pady=10)

    def place_order_from_cart(self):
        cart_id_str = self.order_cart_id_entry.get().strip()
        shipping_type = self.shipping_type_entry.get().strip()
        card_name = self.card_name_entry.get().strip()
        card_number = self.card_number_entry.get().strip()
        card_type = self.card_type_entry.get().strip()
        card_exp = self.card_exp_entry.get().strip()

        if not cart_id_str:
            messagebox.showerror("Error", "Cart ID is required.")
            return

        try:
            cart_id = int(cart_id_str)
        except ValueError:
            messagebox.showerror("Error", "Cart ID must be an integer.")
            return

        # Validate card_exp format if provided
        if card_exp and not self._valid_date(card_exp):
            messagebox.showerror("Error", "Expiration date must be in YYYY-MM-DD format.")
            return

        # Very basic card number sanity check
        if card_number and (not card_number.isdigit() or not 12 <= len(card_number) <= 19):
            messagebox.showerror("Error", "Invalid credit card number format.")
            return

        if not shipping_type:
            shipping_type = None
        if not card_name:
            card_name = None
        if not card_number:
            card_number = None
        if not card_type:
            card_type = None
        if not card_exp:
            card_exp = None  # nullable DATE

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT student_id, cart_status FROM cart WHERE cart_id = %s",
                (cart_id,)
            )
            row = cursor.fetchone()
            if not row:
                messagebox.showerror("Error", f"No cart found with ID {cart_id}.")
                conn.close()
                return

            student_id, cart_status = row
            if cart_status != "Active":
                messagebox.showerror(
                    "Error",
                    f"Cart {cart_id} is not Active (current status: {cart_status})."
                )
                conn.close()
                return

            cursor.execute(
                "SELECT book_id, quantity, unit_price FROM cart_item WHERE cart_id = %s",
                (cart_id,)
            )
            items = cursor.fetchall()
            if not items:
                messagebox.showerror("Error", f"Cart {cart_id} has no items.")
                conn.close()
                return

            cursor.execute(
                """
                INSERT INTO customer_order
                (student_id, shipping_type, credit_card_number,
                 credit_card_exp, credit_card_name, credit_card_type,
                 order_status)
                VALUES (%s, %s, %s, %s, %s, %s, 'Paid')
                """,
                (student_id, shipping_type, card_number, card_exp, card_name, card_type)
            )
            order_id = cursor.lastrowid

            for book_id, quantity, unit_price in items:
                # Create order_item row
                cursor.execute(
                    """
                    INSERT INTO order_item (order_id, book_id, quantity, unit_price)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (order_id, book_id, quantity, unit_price)
                )

                # Track in purchase_history
                cursor.execute(
                    """
                    INSERT INTO purchase_history (student_id, book_id, order_id)
                    VALUES (%s, %s, %s)
                    """,
                    (student_id, book_id, order_id)
                )

            # Now that we've created the order, clear the cart so the student can reuse it
            cursor.execute(
                "DELETE FROM cart_item WHERE cart_id = %s",
                (cart_id,)
            )

            # Keep the same cart record, just mark it Active again
            cursor.execute(
                "UPDATE cart SET cart_status = 'Active' WHERE cart_id = %s",
                (cart_id,)
            )


            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo(
                "Success",
                f"Order {order_id} created from Cart {cart_id}."
            )

            self.order_cart_id_entry.delete(0, tk.END)
            self.shipping_type_entry.delete(0, tk.END)
            self.shipping_type_entry.insert(0, "Standard")
            self.card_name_entry.delete(0, tk.END)
            self.card_number_entry.delete(0, tk.END)
            self.card_type_entry.delete(0, tk.END)
            self.card_type_entry.insert(0, "Visa")
            self.card_exp_entry.delete(0, tk.END)

        except Error as e:
            messagebox.showerror("Database Error", str(e))

    # UPDATE CART (change / remove item)
    def _build_update_cart_section(self, parent):
        separator = tk.Label(parent, text="────────────────────────────────────────")
        separator.pack(pady=10)

        title = tk.Label(
            parent,
            text="Update Cart Item (Change Quantity / Remove)",
            font=("Helvetica", 14, "bold")
        )
        title.pack(pady=5)

        desc = tk.Label(
            parent,
            text="Set new quantity for an item in a cart.\n"
                 "If new quantity is 0, the item will be removed\n"
                 "and inventory will be restored.",
            justify="center"
        )
        desc.pack(pady=5)

        frame = tk.Frame(parent)
        frame.pack(pady=10)

        row_cart = tk.Frame(frame)
        row_cart.pack(fill="x", pady=4)
        tk.Label(row_cart, text="Cart ID", width=16, anchor="w").pack(side="left")
        self.update_cart_id_entry = self._make_int_entry(row_cart, width=25)
        self.update_cart_id_entry.pack(side="left")

        row_book = tk.Frame(frame)
        row_book.pack(fill="x", pady=4)
        tk.Label(row_book, text="Book ID", width=16, anchor="w").pack(side="left")
        self.update_book_id_entry = self._make_int_entry(row_book, width=25)
        self.update_book_id_entry.pack(side="left")

        row_qty = tk.Frame(frame)
        row_qty.pack(fill="x", pady=4)
        tk.Label(row_qty, text="New Quantity", width=16, anchor="w").pack(side="left")
        self.update_quantity_entry = self._make_int_entry(row_qty, width=25)
        self.update_quantity_entry.pack(side="left")

        btn = tk.Button(parent, text="Update Cart Item", command=self.update_cart_item)
        btn.pack(pady=10)

    def update_cart_item(self):
        cart_id_str = self.update_cart_id_entry.get().strip()
        book_id_str = self.update_book_id_entry.get().strip()
        new_qty_str = self.update_quantity_entry.get().strip()

        if not cart_id_str or not book_id_str or not new_qty_str:
            messagebox.showerror("Error", "Cart ID, Book ID, and New Quantity are required.")
            return

        try:
            cart_id = int(cart_id_str)
            book_id = int(book_id_str)
            new_qty = int(new_qty_str)
        except ValueError:
            messagebox.showerror("Error", "All fields must be integers.")
            return

        if new_qty < 0:
            messagebox.showerror("Error", "New quantity cannot be negative.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Get existing cart_item row
            cursor.execute(
                "SELECT quantity FROM cart_item WHERE cart_id = %s AND book_id = %s",
                (cart_id, book_id)
            )
            row = cursor.fetchone()
            if not row:
                cursor.close()
                conn.close()
                messagebox.showerror(
                    "Error",
                    f"No cart item found for cart {cart_id} and book {book_id}."
                )
                return

            old_qty = row[0]

            # If new quantity is 0 -> remove item and restore all inventory
            if new_qty == 0:
                cursor.execute(
                    "UPDATE book SET quantity = quantity + %s WHERE book_id = %s",
                    (old_qty, book_id)
                )
                cursor.execute(
                    "DELETE FROM cart_item WHERE cart_id = %s AND book_id = %s",
                    (cart_id, book_id)
                )
                conn.commit()
                cursor.close()
                conn.close()

                messagebox.showinfo(
                    "Success",
                    f"Item removed from cart {cart_id}. Restored {old_qty} to inventory."
                )
            else:
                if new_qty == old_qty:
                    cursor.close()
                    conn.close()
                    messagebox.showinfo(
                        "No Change",
                        "New quantity is the same as the existing quantity."
                    )
                    return

                diff = new_qty - old_qty  # positive if increasing, negative if decreasing

                if diff > 0:
                    # Need additional inventory
                    cursor.execute(
                        "SELECT quantity FROM book WHERE book_id = %s",
                        (book_id,)
                    )
                    b_row = cursor.fetchone()
                    if not b_row:
                        cursor.close()
                        conn.close()
                        messagebox.showerror("Error", f"No book found with ID {book_id}.")
                        return

                    available = b_row[0]
                    if diff > available:
                        cursor.close()
                        conn.close()
                        messagebox.showerror(
                            "Error",
                            f"Not enough inventory. Only {available} additional units available."
                        )
                        return

                    # Reserve extra copies
                    cursor.execute(
                        "UPDATE book SET quantity = quantity - %s WHERE book_id = %s",
                        (diff, book_id)
                    )
                else:
                    # Decreasing quantity -> return (-diff) copies to inventory
                    cursor.execute(
                        "UPDATE book SET quantity = quantity + %s WHERE book_id = %s",
                        (-diff, book_id)
                    )

                # Update cart_item quantity
                cursor.execute(
                    """
                    UPDATE cart_item
                    SET quantity = %s
                    WHERE cart_id = %s AND book_id = %s
                    """,
                    (new_qty, cart_id, book_id)
                )

                conn.commit()
                cursor.close()
                conn.close()

                messagebox.showinfo(
                    "Success",
                    f"Updated cart {cart_id}, book {book_id} to quantity {new_qty}."
                )

            # Clear entries
            self.update_cart_id_entry.delete(0, tk.END)
            self.update_book_id_entry.delete(0, tk.END)
            self.update_quantity_entry.delete(0, tk.END)

        except Error as e:
            messagebox.showerror("Database Error", str(e))

    # CANCEL ORDER (restore inventory)
    def _build_cancel_order_section(self, parent):
        separator = tk.Label(parent, text="────────────────────────────────────────")
        separator.pack(pady=10)

        title = tk.Label(
            parent,
            text="Cancel Order",
            font=("Helvetica", 14, "bold")
        )
        title.pack(pady=5)

        desc = tk.Label(
            parent,
            text="Cancel an order and return items to inventory.\n"
                 "Allowed only if order is not Shipped/Completed/Cancelled.",
            justify="center"
        )
        desc.pack(pady=5)

        frame = tk.Frame(parent)
        frame.pack(pady=10)

        row_oid = tk.Frame(frame)
        row_oid.pack(fill="x", pady=4)
        tk.Label(row_oid, text="Order ID", width=16, anchor="w").pack(side="left")
        self.cancel_order_id_entry = self._make_int_entry(row_oid, width=25)
        self.cancel_order_id_entry.pack(side="left")

        row_sid = tk.Frame(frame)
        row_sid.pack(fill="x", pady=4)
        tk.Label(row_sid, text="Student ID (optional)", width=16, anchor="w").pack(side="left")
        self.cancel_student_id_entry = self._make_int_entry(row_sid, width=25)
        self.cancel_student_id_entry.pack(side="left")

        btn = tk.Button(parent, text="Cancel Order", command=self.cancel_order)
        btn.pack(pady=10)

    def cancel_order(self):
        order_id_str = self.cancel_order_id_entry.get().strip()
        student_id_str = self.cancel_student_id_entry.get().strip()

        if not order_id_str:
            messagebox.showerror("Error", "Order ID is required.")
            return

        try:
            order_id = int(order_id_str)
        except ValueError:
            messagebox.showerror("Error", "Order ID must be an integer.")
            return

        student_id = None
        if student_id_str:
            try:
                student_id = int(student_id_str)
            except ValueError:
                messagebox.showerror("Error", "Student ID must be an integer.")
                return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT student_id, order_status FROM customer_order WHERE order_id = %s",
                (order_id,)
            )
            row = cursor.fetchone()
            if not row:
                cursor.close()
                conn.close()
                messagebox.showerror("Error", f"No order found with ID {order_id}.")
                return

            db_student_id, status = row

            if student_id is not None and student_id != db_student_id:
                cursor.close()
                conn.close()
                messagebox.showerror(
                    "Error",
                    f"Order {order_id} does not belong to student {student_id}."
                )
                return

            if status in ("Shipped", "Completed", "Cancelled"):
                cursor.close()
                conn.close()
                messagebox.showerror(
                    "Error",
                    f"Order {order_id} cannot be cancelled (status: {status})."
                )
                return

            # Get order items
            cursor.execute(
                "SELECT book_id, quantity FROM order_item WHERE order_id = %s",
                (order_id,)
            )
            items = cursor.fetchall()

            # Restore inventory for each item
            for book_id, qty in items:
                cursor.execute(
                    "UPDATE book SET quantity = quantity + %s WHERE book_id = %s",
                    (qty, book_id)
                )

            # Mark order as cancelled
            cursor.execute(
                """
                UPDATE customer_order
                SET order_status = 'Cancelled'
                WHERE order_id = %s
                """,
                (order_id,)
            )

            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo(
                "Success",
                f"Order {order_id} cancelled and inventory restored."
            )

            self.cancel_order_id_entry.delete(0, tk.END)
            self.cancel_student_id_entry.delete(0, tk.END)

        except Error as e:
            messagebox.showerror("Database Error", str(e))

    # ADD BOOK REVIEW / RATING
    def _build_review_section(self, parent):
        separator = tk.Label(parent, text="────────────────────────────────────────")
        separator.pack(pady=10)

        title = tk.Label(
            parent,
            text="Add Book Review / Rating",
            font=("Helvetica", 14, "bold")
        )
        title.pack(pady=5)

        desc = tk.Label(
            parent,
            text="Create a rating for a book (1–5).\n"
                 "Rating_date is set automatically.",
            justify="center"
        )
        desc.pack(pady=5)

        frame = tk.Frame(parent)
        frame.pack(pady=10)

        row_sid = tk.Frame(frame)
        row_sid.pack(fill="x", pady=4)
        tk.Label(row_sid, text="Student ID", width=16, anchor="w").pack(side="left")
        self.review_student_id_entry = self._make_int_entry(row_sid, width=25)
        self.review_student_id_entry.pack(side="left")

        row_bid = tk.Frame(frame)
        row_bid.pack(fill="x", pady=4)
        tk.Label(row_bid, text="Book ID", width=16, anchor="w").pack(side="left")
        self.review_book_id_entry = self._make_int_entry(row_bid, width=25)
        self.review_book_id_entry.pack(side="left")

        row_rating = tk.Frame(frame)
        row_rating.pack(fill="x", pady=4)
        tk.Label(row_rating, text="Rating (1-5)", width=16, anchor="w").pack(side="left")
        self.review_rating_entry = self._make_int_entry(row_rating, width=25)
        self.review_rating_entry.pack(side="left")

        btn = tk.Button(parent, text="Add Review", command=self.add_review)
        btn.pack(pady=10)

    def add_review(self):
        sid_str = self.review_student_id_entry.get().strip()
        bid_str = self.review_book_id_entry.get().strip()
        rating_str = self.review_rating_entry.get().strip()

        if not sid_str or not bid_str or not rating_str:
            messagebox.showerror("Error", "Student ID, Book ID, and Rating are required.")
            return

        try:
            student_id = int(sid_str)
            book_id = int(bid_str)
            rating = int(rating_str)
        except ValueError:
            messagebox.showerror("Error", "All fields must be integers.")
            return

        if not (1 <= rating <= 5):
            messagebox.showerror("Error", "Rating must be between 1 and 5.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Optional: verify student and book exist
            cursor.execute("SELECT 1 FROM student WHERE student_id = %s", (student_id,))
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                messagebox.showerror("Error", f"No student found with ID {student_id}.")
                return

            cursor.execute("SELECT 1 FROM book WHERE book_id = %s", (book_id,))
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                messagebox.showerror("Error", f"No book found with ID {book_id}.")
                return

            cursor.execute(
                """
                INSERT INTO review (student_id, book_id, rating)
                VALUES (%s, %s, %s)
                """,
                (student_id, book_id, rating)
            )

            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo(
                "Success",
                f"Review added: student {student_id}, book {book_id}, rating {rating}."
            )

            self.review_student_id_entry.delete(0, tk.END)
            self.review_book_id_entry.delete(0, tk.END)
            self.review_rating_entry.delete(0, tk.END)

        except Error as e:
            messagebox.showerror("Database Error", str(e))