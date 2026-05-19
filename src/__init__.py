def __init__(self, master=None):
    super().__init__(master)
    self.title("Student Module")
    self.geometry("550x700")  # Window size; content will scroll

    self._is_macos = (platform.system() == "Darwin")

    # ========= SCROLLABLE CONTAINER =========
    container = tk.Frame(self)
    container.pack(fill="both", expand=True)

    # Use self.canvas so other methods can access it
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

    # Enable mouse wheel / trackpad scrolling (requires _bind_mousewheel helper)
    self._bind_mousewheel(self.canvas)

    # ========= Keep references to entry widgets we need later =========
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

    # ===== Build all sections inside content_frame =====
    self._build_form(self.content_frame)
    self._build_cart_section(self.content_frame)
    self._build_add_book_section(self.content_frame)
    self._build_place_order_section(self.content_frame)
    self._build_update_cart_section(self.content_frame)
    self._build_cancel_order_section(self.content_frame)
    self._build_review_section(self.content_frame)
