# edit_invoice_screen.py
import customtkinter as ctk
from tkinter import messagebox
from db_connection import get_db_connection, update_table_status
import datetime
import os
from PIL import Image

class EditInvoiceScreen:
    def __init__(self, root, role, invoice_id):
        self.root = root
        self.role = role
        self.invoice_id = invoice_id  # Store the invoice ID to edit
        self.root.title("Restaurant Management - Edit Invoice")
        self.root.geometry("1600x900")

        # Styling
        self.blue_accent = "#1E90FF"
        self.light_blue = "#ADD8E6"  # Light blue for border and price background
        self.dark_blue = "#4169E1"
        self.gray = "#CCCCCC"  # Gray for dropdown button background
        self.red = "#FF0000"  # Red for Cancel button
        self.purple = "#800080"  # Purple (no longer used)
        self.magenta = "#FF00FF"  # Magenta (no longer used)
        self.font_large = ("Helvetica", 18, "bold")
        self.font_medium = ("Helvetica", 14)
        self.font_small = ("Helvetica", 12)
        self.font_label = ("Helvetica", 16)
        self.font_button = ("Helvetica", 18, "bold")  # Font for Save and Cancel buttons

        # List to store chosen dishes (dish_id, dish_name, quantity, price)
        self.chosen_dishes = []

        # Total amount
        self.total_amount = 0.0

        # Store the original table ID for "dine in" invoices
        self.original_table_id = None

        # Initialize type_var and table_var here to ensure they exist before load_invoice_data is called
        self.type_var = ctk.StringVar(value="dine in")
        self.table_var = ctk.StringVar(value="")

        # Load add icon
        self.add_icon = None
        try:
            add_icon_path = os.path.join("icons", "add.png")
            if not os.path.exists(add_icon_path):
                raise FileNotFoundError(f"Add icon not found at {add_icon_path}")
            add_icon = Image.open(add_icon_path)
            add_icon = add_icon.resize((40, 40), Image.Resampling.LANCZOS)
            self.add_icon = ctk.CTkImage(light_image=add_icon, dark_image=add_icon, size=(40, 40))
            print("Add icon loaded successfully")
        except Exception as e:
            print(f"Error loading add icon: {e}")
            self.add_icon = None

        # Load search icon
        self.search_icon = None
        try:
            search_icon_path = os.path.join("icons", "search.png")
            if not os.path.exists(search_icon_path):
                raise FileNotFoundError(f"Search icon not found at {search_icon_path}")
            search_icon = Image.open(search_icon_path)
            search_icon = search_icon.resize((30, 30), Image.Resampling.LANCZOS)
            self.search_icon = ctk.CTkImage(light_image=search_icon, dark_image=search_icon, size=(30, 30))
            print("Search icon loaded successfully")
        except Exception as e:
            print(f"Error loading search icon: {e}")
            self.search_icon = None

        # Show edit invoice UI
        self.show_edit_invoice()

    def show_edit_invoice(self):
        print("Starting show_edit_invoice...")

        # Load the invoice data
        if not self.load_invoice_data():
            return  # Exit if loading fails

        # Main Frame
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        print("Main frame packed")

        # Left Panel (Choose Dish Panel)
        left_panel = ctk.CTkFrame(main_frame, fg_color="transparent")
        left_panel.pack(side="left", fill="both", expand=True, padx=20)
        print("Left panel packed")

        # Search Bar
        search_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 10))
        self.search_entry = ctk.CTkEntry(search_frame, width=400, height=40, font=self.font_medium)
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", self.filter_dishes)

        # Search Button with Icon
        search_button = ctk.CTkButton(
            search_frame,
            text="",
            image=self.search_icon,
            command=self.filter_dishes,
            width=40,
            height=40,
            fg_color=self.blue_accent
        )
        search_button.pack(side="left", padx=(5, 0))
        print("Search bar packed")

        # Category Tabs
        self.categories = self.get_categories()
        self.category_var = ctk.StringVar(value="All")  # Default to "All" category
        tabs_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        tabs_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkButton(
            tabs_frame,
            text="All",
            command=lambda: self.set_category("All"),
            font=self.font_medium,
            width=100,
            height=40,
            fg_color=self.blue_accent if self.category_var.get() == "All" else "gray"
        ).pack(side="left", padx=5)
        for category in self.categories:
            category_id, category_name = category
            ctk.CTkButton(
                tabs_frame,
                text=category_name,
                command=lambda cid=category_id, cname=category_name: self.set_category(cname, cid),
                font=self.font_medium,
                width=100,
                height=40,
                fg_color=self.blue_accent if self.category_var.get() == category_name else "gray"
            ).pack(side="left", padx=5)
        print("Category tabs packed")

        # Scrollable frame for dishes (reduced width for 3 items per row)
        self.dishes_scrollable_frame = ctk.CTkScrollableFrame(left_panel, fg_color="transparent", width=700, height=500)
        self.dishes_scrollable_frame.pack(fill="both", expand=True)
        print("Dishes scrollable frame packed")

        # Inner frame to hold the dish grid
        self.dishes_frame = ctk.CTkFrame(self.dishes_scrollable_frame, fg_color="transparent")
        self.dishes_frame.pack(fill="both", expand=True)
        print("Dishes frame packed")

        # Load initial dishes
        self.filter_dishes()  # Call filter_dishes to load initial dishes

        # Right Panel (Choose Type and Chosen Dishes)
        right_panel = ctk.CTkFrame(main_frame, width=400, fg_color="transparent")
        right_panel.pack(side="right", fill="both", expand=True, padx=20)
        print("Right panel packed")

        # Frame for Type and Table Dropdowns (on the same row)
        dropdown_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        dropdown_frame.pack(fill="x", pady=(10, 0))

        # Type Dropdown (with box and padding)
        type_box = ctk.CTkFrame(dropdown_frame, fg_color="white", border_width=2, border_color=self.blue_accent)
        type_box.pack(side="left", padx=(0, 30))
        type_label = ctk.CTkLabel(type_box, text="Type:", font=self.font_label)
        type_label.pack(side="left", padx=(15, 10), pady=5)
        self.type_dropdown = ctk.CTkComboBox(
            type_box,
            values=["dine in", "take away", "delivery"],
            variable=self.type_var,
            width=150,
            height=40,
            font=self.font_medium,
            fg_color="white",
            button_color=self.gray,
            command=self.toggle_table_dropdown
        )
        self.type_dropdown.pack(side="left", padx=(0, 15), pady=5)
        print("Invoice type dropdown packed")

        # Table Dropdown (with box and padding)
        table_box = ctk.CTkFrame(dropdown_frame, fg_color="white", border_width=2, border_color=self.blue_accent)
        table_box.pack(side="left")
        self.table_label = ctk.CTkLabel(table_box, text="Table:", font=self.font_label)
        self.table_label.pack(side="left", padx=(15, 10), pady=5)
        self.table_dropdown = ctk.CTkComboBox(
            table_box,
            values=self.get_available_tables(),
            variable=self.table_var,
            width=150,
            height=40,
            font=self.font_medium,
            fg_color="white",
            button_color=self.gray
        )
        self.table_dropdown.pack(side="left", padx=(0, 15), pady=5)
        print("Table dropdown packed")

        # Chosen Dishes List (with light blue border and padding)
        self.chosen_scrollable_frame = ctk.CTkFrame(
            right_panel,
            fg_color="white",
            border_width=2,
            border_color=self.light_blue,
            width=350
        )
        self.chosen_scrollable_frame.pack(fill="both", expand=True, pady=(30, 30))
        print("Chosen dishes frame packed")

        self.chosen_inner_frame = ctk.CTkFrame(self.chosen_scrollable_frame, fg_color="white")
        self.chosen_inner_frame.pack(fill="both", expand=True, padx=15, pady=15)
        print("Chosen dishes inner frame packed")

        self.chosen_frame = ctk.CTkScrollableFrame(self.chosen_inner_frame, fg_color="white")
        self.chosen_frame.pack(fill="both", expand=True)
        print("Chosen dishes scrollable frame packed")

        # Total Price (with box and padding)
        total_box = ctk.CTkFrame(right_panel, fg_color="white", border_width=2, border_color=self.blue_accent)
        total_box.pack(fill="x", pady=(10, 0))
        total_label = ctk.CTkLabel(total_box, text="Total Price:", font=self.font_label)
        total_label.pack(side="left", padx=(15, 0), pady=5)
        self.total_price_label = ctk.CTkLabel(total_box, text=f"${self.total_amount:.2f}", font=self.font_label)
        self.total_price_label.pack(side="right", padx=(0, 15), pady=5)
        print("Total price label packed")

        # Frame for Save and Cancel Buttons (on the same row, fixed width)
        button_frame = ctk.CTkFrame(right_panel, fg_color="transparent", width=350, height=70)
        button_frame.pack(fill="x", pady=(10, 10))
        button_frame.pack_propagate(False)  # Prevent the frame from shrinking

        # Save Button
        save_button = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save_invoice,
            height=50,
            font=self.font_button,
            fg_color=self.blue_accent
        )
        save_button.pack(side="left", expand=True, fill="x", padx=(0, 5))

        # Cancel Button (red)
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.back_to_main,
            height=50,
            font=self.font_button,
            fg_color=self.red
        )
        cancel_button.pack(side="left", expand=True, fill="x", padx=(5, 0))

        print("Save and Cancel buttons packed")

        # Update the UI based on the loaded invoice data
        self.toggle_table_dropdown(self.type_var.get())
        self.update_chosen_dishes()

    def load_invoice_data(self):
        """Load the invoice data based on the invoice_id."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Load invoice details
            cursor.execute("SELECT table_id, total_amount, type, status FROM invoices WHERE id = ?", (self.invoice_id,))
            invoice = cursor.fetchone()
            if not invoice:
                messagebox.showerror("Error", f"Invoice with ID {self.invoice_id} not found.")
                conn.close()
                self.back_to_main()
                return False

            table_id, total_amount, invoice_type, status = invoice
            self.total_amount = total_amount
            self.type_var.set(invoice_type)

            # Store the original table ID for "dine in" invoices
            self.original_table_id = table_id if invoice_type == "dine in" else None

            # Set the table number if the invoice type is "dine in"
            if invoice_type == "dine in" and table_id:
                cursor.execute("SELECT table_number FROM tables WHERE id = ?", (table_id,))
                table_number = cursor.fetchone()
                if table_number:
                    self.table_var.set(str(table_number[0]))
                else:
                    self.table_var.set("")
            else:
                self.table_var.set("")

            # Load invoice items (chosen dishes)
            cursor.execute("""
                SELECT di.id, di.name, ii.quantity, di.price
                FROM invoice_items ii
                JOIN dishes di ON ii.dish_id = di.id
                WHERE ii.invoice_id = ?
            """, (self.invoice_id,))
            invoice_items = cursor.fetchall()

            self.chosen_dishes = [[dish_id, dish_name, quantity, price] for dish_id, dish_name, quantity, price in invoice_items]

            conn.close()
            return True
        except Exception as e:
            print(f"Error loading invoice data: {e}")
            messagebox.showerror("Error", f"Failed to load invoice data: {e}")
            if 'conn' in locals():
                conn.close()
            self.back_to_main()
            return False

    def get_available_tables(self):
        """Fetch available tables (status = 'empty') excluding the current table if it exists."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = "SELECT id, table_number FROM tables WHERE status = 'empty'"
            params = []
            if self.original_table_id:
                query += " OR id = ?"
                params.append(self.original_table_id)
            cursor.execute(query, params)
            tables = cursor.fetchall()
            conn.close()
            # Return table numbers as strings for the dropdown
            return [str(table[1]) for table in tables]
        except Exception as e:
            print(f"Error fetching tables: {e}")
            messagebox.showerror("Error", f"Failed to fetch tables: {e}")
            return []

    def get_categories(self):
        """Fetch all categories."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM categories")
            categories = cursor.fetchall()
            conn.close()
            return categories
        except Exception as e:
            print(f"Error fetching categories: {e}")
            messagebox.showerror("Error", f"Failed to fetch categories: {e}")
            return []

    def get_dishes(self, category_id=None, search_query=""):
        """Fetch dishes, optionally filtered by category and search query."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = "SELECT id, name, price, img_path FROM dishes WHERE 1=1"
            params = []
            if category_id and category_id != "All":
                query += " AND category_id = ?"
                params.append(category_id)
            if search_query:
                query += " AND name LIKE ?"
                params.append(f"%{search_query}%")
            cursor.execute(query, params)
            dishes = cursor.fetchall()
            conn.close()
            return dishes
        except Exception as e:
            print(f"Error fetching dishes: {e}")
            messagebox.showerror("Error", f"Failed to fetch dishes: {e}")
            return []

    def set_category(self, category_name, category_id=None):
        """Set the current category and refresh the dishes."""
        self.category_var.set(category_name)
        self.filter_dishes()

        # Update tab colors
        for widget in self.root.winfo_children()[0].winfo_children()[0].winfo_children()[1].winfo_children():
            if isinstance(widget, ctk.CTkButton):
                widget.configure(fg_color=self.blue_accent if widget.cget("text") == category_name else "gray")

    def filter_dishes(self, event=None):
        """Filter dishes based on category and search query."""
        category_name = self.category_var.get()
        category_id = None
        if category_name != "All":
            for cid, cname in self.categories:
                if cname == category_name:
                    category_id = cid
                    break
        search_query = self.search_entry.get().strip()
        dishes = self.get_dishes(category_id, search_query)
        self.display_dishes(dishes)

    def display_dishes(self, dishes):
        """Display dishes in a grid (3 per row)."""
        # Clear the current dishes
        for widget in self.dishes_frame.winfo_children():
            widget.destroy()

        # Ensure dishes_frame expands to fit all dishes
        num_rows = (len(dishes) + 2) // 3  # Calculate required rows (3 dishes per row)
        required_height = num_rows * 190  # Reduced height per row (150 height + 20 pady on each side)
        self.dishes_frame.configure(height=required_height)
        print(f"Dishes frame height set to {required_height} for {num_rows} rows")

        # Display dishes in a grid (3 per row)
        for idx, (dish_id, dish_name, price, img_path) in enumerate(dishes):
            row = idx // 3  # 3 dishes per row
            col = idx % 3

            # Dish Frame (with light blue border)
            dish_frame = ctk.CTkFrame(
                self.dishes_frame,
                fg_color="#F0F8FF",
                border_width=2,
                border_color=self.light_blue,
                width=150,
                height=150
            )
            dish_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            dish_frame.grid_propagate(False)

            # Dish Image
            if img_path and os.path.exists(img_path):
                try:
                    img = Image.open(img_path)
                    img = img.resize((80, 80), Image.Resampling.LANCZOS)
                    dish_img = ctk.CTkImage(light_image=img, dark_image=img, size=(80, 80))
                    img_label = ctk.CTkLabel(dish_frame, image=dish_img, text="")
                    img_label.pack(pady=(5, 0))
                except Exception as e:
                    print(f"Error loading image for dish {dish_id}: {e}")
                    img_label = ctk.CTkLabel(dish_frame, text="No Image", font=self.font_small)
                    img_label.pack(pady=(5, 0))
            else:
                img_label = ctk.CTkLabel(dish_frame, text="No Image", font=self.font_small)
                img_label.pack(pady=(5, 0))

            # Frame for Dish Name and Price (on the same row, transparent background)
            name_price_frame = ctk.CTkFrame(dish_frame, fg_color="transparent")
            name_price_frame.pack(fill="x", padx=5, pady=5)

            # Dish Name (no border)
            name_label = ctk.CTkLabel(
                name_price_frame,
                text=dish_name,
                font=self.font_small,
                text_color="black"
            )
            name_label.pack(side="left")

            # Frame for Price (with blue border, light blue background, white text, padding)
            price_border_frame = ctk.CTkFrame(
                name_price_frame,
                fg_color=self.light_blue,
                border_width=2,
                border_color=self.blue_accent,
                corner_radius=5
            )
            price_border_frame.pack(side="right")
            price_label = ctk.CTkLabel(
                price_border_frame,
                text=f"${price:.2f}",
                font=self.font_small,
                text_color="white"
            )
            price_label.pack(padx=5, pady=2)

            # Add Button (full width)
            add_button = ctk.CTkButton(
                master=dish_frame,
                text="" if self.add_icon else "Add",
                image=self.add_icon,
                command=lambda did=dish_id, dname=dish_name, dprice=price: self.add_dish(did, dname, dprice),
                height=40,
                fg_color=self.blue_accent
            )
            add_button.pack(fill="x", padx=5, pady=(5, 5))

        # Configure grid weights
        for i in range(num_rows):
            self.dishes_frame.grid_rowconfigure(i, weight=1, minsize=190)
        for j in range(3):  # 3 columns
            self.dishes_frame.grid_columnconfigure(j, weight=1, minsize=170)
        self.dishes_frame.grid_propagate(False)

    def add_dish(self, dish_id, dish_name, price):
        """Add a dish to the chosen dishes list with default quantity 1."""
        # Check if the dish is already in the list
        for item in self.chosen_dishes:
            if item[0] == dish_id:
                # Increase quantity if dish already exists
                item[2] += 1
                self.update_chosen_dishes()
                return

        # Add new dish with quantity 1
        self.chosen_dishes.append([dish_id, dish_name, 1, price])
        self.update_chosen_dishes()

    def update_chosen_dishes(self):
        """Update the display of chosen dishes and total amount."""
        # Clear the current display
        for widget in self.chosen_frame.winfo_children():
            widget.destroy()

        # Calculate total amount
        self.total_amount = 0.0
        for dish in self.chosen_dishes:
            dish_id, dish_name, quantity, price = dish
            self.total_amount += price * quantity

            # Calculate total price for this item
            item_total = quantity * price

            # Frame for each chosen dish with a slight border and padding
            dish_frame = ctk.CTkFrame(self.chosen_frame, fg_color="#F0F8FF", border_width=1, border_color="#CCCCCC")
            dish_frame.pack(fill="x", pady=10, padx=10)

            # Dish Name (left)
            name_label = ctk.CTkLabel(dish_frame, text=dish_name, font=self.font_medium, text_color="black")
            name_label.pack(side="left", padx=(15, 0))

            # Total Price for this item (right)
            item_total_label = ctk.CTkLabel(dish_frame, text=f"${item_total:.2f}", font=self.font_medium, text_color="black")
            item_total_label.pack(side="right", padx=15)

            # Quantity Frame (right, just before the total price)
            qty_frame = ctk.CTkFrame(dish_frame, fg_color="transparent")
            qty_frame.pack(side="right", padx=5)

            # Decrease Quantity Button (left of quantity)
            minus_button = ctk.CTkButton(
                qty_frame,
                text="-",
                command=lambda did=dish_id: self.change_quantity(did, -1),
                width=30,
                height=30,
                font=self.font_small,
                fg_color=self.blue_accent
            )
            minus_button.pack(side="left", padx=5)

            # Quantity (middle)
            qty_label = ctk.CTkLabel(qty_frame, text=str(quantity), font=self.font_medium, text_color="black")
            qty_label.pack(side="left", padx=5)

            # Increase Quantity Button (right of quantity)
            plus_button = ctk.CTkButton(
                qty_frame,
                text="+",
                command=lambda did=dish_id: self.change_quantity(did, 1),
                width=30,
                height=30,
                font=self.font_small,
                fg_color=self.blue_accent
            )
            plus_button.pack(side="left", padx=5)

        # Update total price label
        self.total_price_label.configure(text=f"${self.total_amount:.2f}")

    def change_quantity(self, dish_id, change):
        """Increase or decrease the quantity of a chosen dish."""
        for item in self.chosen_dishes:
            if item[0] == dish_id:
                item[2] += change
                if item[2] <= 0:
                    self.chosen_dishes.remove(item)
                break
        self.update_chosen_dishes()

    def toggle_table_dropdown(self, choice):
        """Enable/disable table dropdown based on invoice type."""
        if choice == "dine in":
            self.table_dropdown.configure(state="normal")
            self.table_label.configure(state="normal")
            # Refresh available tables
            self.table_dropdown.configure(values=self.get_available_tables())
            if not self.table_var.get():
                self.table_var.set("")
        else:
            self.table_dropdown.configure(state="disabled")
            self.table_label.configure(state="disabled")
            self.table_var.set("")

    def save_invoice(self):
        """Update the invoice and its items in the database."""
        invoice_type = self.type_var.get()
        table_number = self.table_var.get()

        # Validate invoice items
        if not self.chosen_dishes:
            messagebox.showerror("Error", "Please add at least one item to the invoice.")
            return

        # Validate table for 'dine in' invoices
        table_id = None
        if invoice_type == "dine in":
            if not table_number:
                messagebox.showerror("Error", "Please select a table for a 'dine in' invoice.")
                return
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM tables WHERE table_number = ? AND (status = 'empty' OR id = ?)", (int(table_number), self.original_table_id))
                result = cursor.fetchone()
                if not result:
                    messagebox.showerror("Error", "Selected table is not available.")
                    conn.close()
                    return
                table_id = result[0]
            except Exception as e:
                print(f"Error fetching table: {e}")
                messagebox.showerror("Error", f"Failed to fetch table: {e}")
                conn.close()
                return
        else:
            conn = get_db_connection()
            cursor = conn.cursor()

        # Update the invoice
        try:
            # Update the invoice details
            cursor.execute(
                "UPDATE invoices SET table_id = ?, total_amount = ?, type = ? WHERE id = ?",
                (table_id, self.total_amount, invoice_type, self.invoice_id)
            )

            # Delete existing invoice items
            cursor.execute("DELETE FROM invoice_items WHERE invoice_id = ?", (self.invoice_id,))

            # Insert updated invoice items
            for item in self.chosen_dishes:
                dish_id, _, quantity, _ = item
                cursor.execute(
                    "INSERT INTO invoice_items (invoice_id, dish_id, quantity) VALUES (?, ?, ?)",
                    (self.invoice_id, dish_id, quantity)
                )

            # Update table status for 'dine in' invoices
            if invoice_type == "dine in":
                # If the table has changed, update the old table status
                if self.original_table_id and self.original_table_id != table_id:
                    cursor.execute("UPDATE tables SET status = 'empty' WHERE id = ?", (self.original_table_id,))
                # Update the new table status
                if table_id:
                    update_table_status(table_id, conn)
            else:
                # If the invoice type is no longer "dine in", free the original table
                if self.original_table_id:
                    cursor.execute("UPDATE tables SET status = 'empty' WHERE id = ?", (self.original_table_id,))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Invoice updated successfully!")
            self.back_to_main()

        except Exception as e:
            print(f"Error updating invoice: {e}")
            messagebox.showerror("Error", f"Failed to update invoice: {e}")
            if 'conn' in locals():
                conn.close()

    def back_to_main(self):
        try:
            from main_screen import MainScreen
            for widget in self.root.winfo_children():
                widget.destroy()
            MainScreen(self.root, self.role)
        except Exception as e:
            print(f"Error in back_to_main: {e}")
            messagebox.showerror("Error", f"Failed to return to main screen: {e}")