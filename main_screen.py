import customtkinter as ctk
from tkinter import messagebox
from db_connection import get_db_connection, update_table_status
from manage_staffs import ManageStaffs
from menu_screen import MenuScreen
from table_management_screen import TableManagementScreen
from add_invoice_screen import AddInvoiceScreen
from edit_invoice_screen import EditInvoiceScreen
from paid_invoices_screen import PaidInvoicesScreen
import os
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import datetime
import platform
import subprocess

class MainScreen:
    def __init__(self, root, role):
        self.root = root
        self.role = role
        self.root.title(f"Restaurant Management - {role.capitalize()}")
        window_width = 1600
        window_height = 900
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.primary_color = "#9ACBD0"
        self.primary_dark = "#006A71"
        self.accent_color = "#9ACBD0"
        self.accent_dark = "#006A71"
        self.background_start = "#F2EFE7"
        self.background_end = "#E8E4D9"
        self.text_color = "#48A6A7"
        self.header_color = "#006A71"
        self.dine_in_color = "#1E90FF"
        self.take_away_color = "#FFA500"
        self.delivery_color = "#800080"
        self.dark_gray = "#333333"
        self.price_green = "#006A71"
        self.price_green_light = "#D1E8E8"
        self.delete_color = "#FF6F61"
        self.delete_dark = "#D94F43"
        self.bank_color = "#9ACBD0"
        self.bank_dark = "#006A71"
        self.card_color = "#9ACBD0"
        self.card_dark = "#006A71"
        self.print_color = "#9ACBD0"
        self.print_dark = "#006A71"
        self.row_color_1 = "#F9F7F0"
        self.row_color_2 = "#EFEBE0"
        self.hover_color = "#D1E8E8"
        self.selected_color = "#48A6A7"
        self.shadow_color = "#D3CFC3"
        self.font_title = ("Helvetica", 24, "bold")
        self.font_header = ("Helvetica", 18, "bold")
        self.font_medium = ("Helvetica", 16)
        self.font_medium_bold = ("Helvetica", 16, "bold")
        self.font_small = ("Helvetica", 14)
        self.font_small_bold = ("Helvetica", 14, "bold")
        self.font_button = ("Helvetica", 16, "bold")
        self.font_id = ("Helvetica", 18, "bold")
        self.font_type = ("Helvetica", 16, "italic")
        self.font_price = ("Helvetica", 14, "bold")
        self.font_total = ("Helvetica", 18, "bold")
        self.font_total_amount = ("Helvetica", 16, "bold")
        self.font_dialog_title = ("Helvetica", 22, "bold")
        self.font_payment_button = ("Helvetica", 14, "bold")
        self.payment_icons = {}
        icon_names = ["cash.png", "bank.png", "card.png"]
        for icon_name in icon_names:
            try:
                icon_path = os.path.join("icons", icon_name)
                if not os.path.exists(icon_path):
                    raise FileNotFoundError
                icon = Image.open(icon_path)
                icon = icon.resize((40, 40), Image.Resampling.LANCZOS)
                self.payment_icons[icon_name] = ctk.CTkImage(light_image=icon, dark_image=icon, size=(40, 40))
            except Exception as e:
                self.payment_icons[icon_name] = None
        self.edit_icon = None
        try:
            edit_icon_path = os.path.join("icons", "edit.png")
            if not os.path.exists(edit_icon_path):
                raise FileNotFoundError
            edit_icon = Image.open(edit_icon_path)
            edit_icon = edit_icon.resize((30, 30), Image.Resampling.LANCZOS)
            self.edit_icon = ctk.CTkImage(light_image=edit_icon, dark_image=edit_icon, size=(30, 30))
        except Exception as e:
            self.edit_icon = None
        self.print_icon = None
        try:
            print_icon_path = os.path.join("icons", "print.png")
            if not os.path.exists(print_icon_path):
                raise FileNotFoundError
            print_icon = Image.open(print_icon_path)
            print_icon = print_icon.resize((30, 30), Image.Resampling.LANCZOS)
            self.print_icon = ctk.CTkImage(light_image=print_icon, dark_image=print_icon, size=(30, 30))
        except Exception as e:
            self.print_icon = None
        self.delete_icon = None
        try:
            delete_icon_path = os.path.join("icons", "delete.png")
            if not os.path.exists(delete_icon_path):
                raise FileNotFoundError
            delete_icon = Image.open(delete_icon_path)
            delete_icon = delete_icon.resize((30, 30), Image.Resampling.LANCZOS)
            self.delete_icon = ctk.CTkImage(light_image=delete_icon, dark_image=delete_icon, size=(30, 30))
        except Exception as e:
            self.delete_icon = None
        self.show_main_app()

    def darken_color(self, hex_color):
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = max(0, int(r * 0.8))
        g = max(0, int(g * 0.8))
        b = max(0, int(b * 0.8))
        return f"#{r:02x}{g:02x}{b:02x}"

    def on_invoice_enter(self, event, frame, original_border_color, original_bg_color):
        darkened_border = self.darken_color(original_border_color)
        darkened_bg = self.darken_color(original_bg_color)
        frame.configure(border_color=darkened_border, fg_color=(darkened_bg, self.darken_color(self.background_end)))

    def on_invoice_leave(self, event, frame, original_border_color, original_bg_color):
        frame.configure(border_color=original_border_color, fg_color=(original_bg_color, self.background_end))

    def on_edit_enter(self, event, button):
        button.configure(fg_color=self.darken_color(self.primary_color))

    def on_edit_leave(self, event, button):
        button.configure(fg_color=self.primary_color)

    def on_action_button_enter(self, event, button, original_gradient_start, original_gradient_end):
        darkened_start = self.darken_color(original_gradient_start)
        darkened_end = self.darken_color(original_gradient_end)
        button.configure(fg_color=(darkened_start, darkened_end))

    def on_action_button_leave(self, event, button, original_gradient_start, original_gradient_end):
        button.configure(fg_color=(original_gradient_start, original_gradient_end))

    def on_payment_button_enter(self, event, button, original_gradient_start, original_gradient_end):
        darkened_start = self.darken_color(original_gradient_start)
        darkened_end = self.darken_color(original_gradient_end)
        button.configure(fg_color=(darkened_start, darkened_end))

    def on_payment_button_leave(self, event, button, original_gradient_start, original_gradient_end):
        button.configure(fg_color=(original_gradient_start, original_gradient_end))

    def on_dish_row_enter(self, event, frame):
        frame.configure(fg_color=self.hover_color)

    def on_dish_row_leave(self, event, frame, original_color):
        frame.configure(fg_color=original_color)

    def show_main_app(self):
        main_frame = ctk.CTkFrame(self.root, fg_color=(self.background_start, self.background_end))
        main_frame.pack(fill="both", expand=True)
        top_bar = ctk.CTkFrame(main_frame, fg_color="transparent", height=60)
        top_bar.pack(fill="x", padx=20, pady=(10, 0))
        title_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        title_frame.pack(side="left", padx=20)
        try:
            logo_path = os.path.join("icons", "logo.png")
            if not os.path.exists(logo_path):
                raise FileNotFoundError
            logo_image = Image.open(logo_path)
            logo_image = logo_image.resize((40, 40), Image.Resampling.LANCZOS)
            logo_ctk_image = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(40, 40))
            ctk.CTkLabel(title_frame, image=logo_ctk_image, text="").pack(side="left", padx=(0, 10))
        except Exception as e:
            ctk.CTkLabel(
                title_frame,
                text="🍽️",
                font=("Helvetica", 40),
                text_color=self.header_color
            ).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(
            title_frame,
            text="Restaurant Sales Management",
            font=self.font_title,
            text_color=self.header_color
        ).pack(side="left")
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        left_panel = ctk.CTkFrame(content_frame, width=250, fg_color="transparent")
        left_panel.pack(side="left", fill="y", padx=20, pady=20)
        ctk.CTkLabel(left_panel, text=f"Welcome, {self.role}!", font=self.font_header, text_color=self.header_color).pack(pady=30)
        button_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        button_frame.pack()
        if self.role == "admin":
            ctk.CTkButton(
                button_frame,
                text="Manage Staffs",
                command=self.show_manage_staffs,
                font=self.font_button,
                width=220,
                height=50,
                fg_color=(self.primary_color, self.primary_dark),
                text_color="white",
                corner_radius=10
            ).pack(pady=15)
        ctk.CTkButton(
            button_frame,
            text="Menu",
            command=self.show_menu,
            font=self.font_button,
            width=220,
            height=50,
            fg_color=(self.primary_color, self.primary_dark),
            text_color="white",
            corner_radius=10
        ).pack(pady=15)
        ctk.CTkButton(
            button_frame,
            text="Manage Tables",
            command=self.show_table_management,
            font=self.font_button,
            width=220,
            height=50,
            fg_color=(self.primary_color, self.primary_dark),
            text_color="white",
            corner_radius=10
        ).pack(pady=15)
        ctk.CTkButton(
            button_frame,
            text="Paid Invoices",
            command=self.show_paid_invoices,
            font=self.font_button,
            width=220,
            height=50,
            fg_color=(self.primary_color, self.primary_dark),
            text_color="white",
            corner_radius=10
        ).pack(pady=15)
        spacer = ctk.CTkFrame(left_panel, fg_color="transparent")
        spacer.pack(fill="y", expand=True)
        logout_button = ctk.CTkButton(
            button_frame,
            text="Logout",
            font=self.font_button,
            fg_color=(self.delete_color, self.delete_dark),
            text_color="white",
            width=220,
            height=50,
            corner_radius=10,
            command=self.logout
        )
        logout_button.pack(pady=(30, 15))
        logout_button.bind("<Enter>", lambda event, b=logout_button: self.on_action_button_enter(event, b, self.delete_color, self.delete_dark))
        logout_button.bind("<Leave>", lambda event, b=logout_button: self.on_action_button_leave(event, b, self.delete_color, self.delete_dark))
        for button in button_frame.winfo_children():
            if button != logout_button:
                button.bind("<Enter>", lambda event, b=button: self.on_action_button_enter(event, b, self.primary_color, self.primary_dark))
                button.bind("<Leave>", lambda event, b=button: self.on_action_button_leave(event, b, self.primary_color, self.primary_dark))
        middle_panel = ctk.CTkFrame(content_frame, fg_color="transparent")
        middle_panel.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        self.scrollable_frame = ctk.CTkScrollableFrame(
            middle_panel,
            fg_color=(self.row_color_1, self.row_color_2),
            width=775,
            height=540,
            corner_radius=15,
            border_width=2,
            border_color=(self.primary_color, self.primary_dark)
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.invoices_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.invoices_frame.pack(fill="both", expand=True)
        self.load_invoices()
        add_order_button = ctk.CTkButton(
            middle_panel,
            text="Add new order",
            command=self.show_add_invoice,
            font=self.font_button,
            width=775,
            height=60,
            fg_color=(self.accent_color, self.accent_dark),
            text_color="black",
            corner_radius=10,
            border_width=1,
            border_color=self.accent_dark
        )
        add_order_button.pack(pady=(20, 20))
        add_order_button.bind("<Enter>", lambda event, b=add_order_button: self.on_action_button_enter(event, b, self.accent_color, self.accent_dark))
        add_order_button.bind("<Leave>", lambda event, b=add_order_button: self.on_action_button_leave(event, b, self.accent_color, self.accent_dark))
        self.right_panel = ctk.CTkFrame(content_frame, width=425, fg_color="transparent")
        self.right_panel.pack(side="left", fill="both", expand=False, padx=20, pady=20)
        self.details_frame = ctk.CTkFrame(
            self.right_panel,
            width=425,
            height=600,
            fg_color=(self.row_color_1, self.row_color_2),
            border_width=2,
            border_color=(self.primary_color, self.primary_dark),
            corner_radius=15
        )
        self.details_frame.pack(pady=(20, 0))
        self.details_frame.pack_propagate(False)
        self.details_label = ctk.CTkLabel(self.details_frame, text="Invoice Details", font=self.font_header, text_color=self.header_color)
        self.details_label.pack(pady=20)
        self.action_button_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent", width=425)
        self.action_button_frame.pack(fill="x", pady=(10, 0))
        self.action_button_frame.pack_propagate(False)

    def load_invoices(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT i.id, i.table_id, i.total_amount, i.type, t.table_number
                FROM invoices i
                LEFT JOIN tables t ON i.table_id = t.id
                WHERE i.status = 'unpaid'
            ''')
            invoices = cursor.fetchall()
            conn.close()
            for widget in self.invoices_frame.winfo_children():
                widget.destroy()
            num_rows = (len(invoices) + 2) // 3
            required_height = num_rows * 240
            self.invoices_frame.configure(height=required_height)
            invoice_frames = []
            for idx, (invoice_id, table_id, total_amount, invoice_type, table_number) in enumerate(invoices):
                row = idx // 3
                col = idx % 3
                border_color = self.dine_in_color if invoice_type == "dine in" else \
                              self.take_away_color if invoice_type == "take away" else \
                              self.delivery_color
                invoice_frame = ctk.CTkFrame(
                    self.invoices_frame,
                    fg_color=(self.background_start, self.background_end),
                    width=200,
                    height=200,
                    border_width=2,
                    border_color=border_color,
                    corner_radius=12
                )
                invoice_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                invoice_frame.grid_propagate(False)
                invoice_frames.append((invoice_id, invoice_frame))
                invoice_frame.bind("<Enter>", lambda event, f=invoice_frame, bc=border_color, bg=self.background_start: self.on_invoice_enter(event, f, bc, bg))
                invoice_frame.bind("<Leave>", lambda event, f=invoice_frame, bc=border_color, bg=self.background_start: self.on_invoice_leave(event, f, bc, bg))
                invoice_frame.bind("<Button-1>", lambda event, inv_id=invoice_id: self.display_invoice_details(inv_id))
                id_label = ctk.CTkLabel(
                    invoice_frame,
                    text=f"#{invoice_id}",
                    font=self.font_id,
                    text_color=self.dark_gray,
                    fg_color=(self.row_color_1, self.row_color_2),
                    corner_radius=5,
                    padx=5,
                    pady=2
                )
                id_label.pack(pady=(20, 0))
                id_label.bind("<Button-1>", lambda event, inv_id=invoice_id: self.display_invoice_details(inv_id))
                display_type = f"{invoice_type.title()} - Table {table_number}" if invoice_type == "dine in" and table_number else invoice_type.title()
                type_frame = ctk.CTkFrame(invoice_frame, fg_color="transparent")
                type_frame.pack(pady=(10, 0))
                type_label = ctk.CTkLabel(
                    type_frame,
                    text=display_type,
                    font=self.font_type,
                    text_color=border_color
                )
                type_label.pack()
                underline = ctk.CTkFrame(type_frame, fg_color=border_color, height=2)
                underline.pack(fill="x", padx=5)
                type_label.bind("<Button-1>", lambda event, inv_id=invoice_id: self.display_invoice_details(inv_id))
                underline.bind("<Button-1>", lambda event, inv_id=invoice_id: self.display_invoice_details(inv_id))
                price_label = ctk.CTkLabel(
                    invoice_frame,
                    text=f"Total Price: ${total_amount:.2f}",
                    font=self.font_price,
                    text_color=self.price_green,
                    fg_color=(self.row_color_1, self.row_color_2),
                    corner_radius=5,
                    padx=5,
                    pady=2
                )
                price_label.pack(pady=(20, 0))
                price_label.bind("<Button-1>", lambda event, inv_id=invoice_id: self.display_invoice_details(inv_id))
                edit_button = ctk.CTkButton(
                    master=invoice_frame,
                    text="" if self.edit_icon else "Edit",
                    image=self.edit_icon,
                    command=lambda inv_id=invoice_id: self.show_edit_invoice(inv_id),
                    width=40,
                    height=40,
                    fg_color=self.primary_color,
                    corner_radius=10
                )
                edit_button.pack(pady=(10, 10))
                edit_button.bind("<Enter>", lambda event, b=edit_button: self.on_edit_enter(event, b))
                edit_button.bind("<Leave>", lambda event, b=edit_button: self.on_edit_leave(event, b))
            for i in range((len(invoices) + 2) // 3):
                self.invoices_frame.grid_rowconfigure(i, weight=1, minsize=240)
            for j in range(3):
                self.invoices_frame.grid_columnconfigure(j, weight=1, minsize=220)
            self.invoices_frame.grid_propagate(False)
            self.root.update()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load invoices: {e}")

    def display_invoice_details(self, invoice_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT i.id, i.table_id, i.total_amount, i.type, i.timestamp, i.status, t.table_number
                FROM invoices i
                LEFT JOIN tables t ON i.table_id = t.id
                WHERE i.id = ?
            ''', (invoice_id,))
            invoice = cursor.fetchone()
            if not invoice:
                messagebox.showerror("Error", f"Invoice with ID {invoice_id} not found.")
                conn.close()
                return
            invoice_id, table_id, total_amount, invoice_type, timestamp, status, table_number = invoice
            cursor.execute('''
                SELECT di.name, ii.quantity, di.price
                FROM invoice_items ii
                JOIN dishes di ON ii.dish_id = di.id
                WHERE ii.invoice_id = ?
            ''', (invoice_id,))
            items = cursor.fetchall()
            conn.close()
            for widget in self.details_frame.winfo_children():
                widget.destroy()
            for widget in self.action_button_frame.winfo_children():
                widget.destroy()
            border_color = self.dine_in_color if invoice_type == "dine in" else \
                          self.take_away_color if invoice_type == "take away" else \
                          self.delivery_color
            id_label = ctk.CTkLabel(
                self.details_frame,
                text=f"Invoice #{invoice_id}",
                font=("Helvetica", 24, "bold"),
                text_color=(self.header_color, border_color),
                fg_color=(self.row_color_1, self.row_color_2),
                corner_radius=8,
                padx=10,
                pady=5
            )
            id_label.pack(pady=(10, 15))
            details_frame = ctk.CTkFrame(self.details_frame, fg_color="transparent")
            details_frame.pack(fill="x", padx=20)
            type_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
            type_frame.pack(fill="x", pady=(0, 5))
            ctk.CTkLabel(type_frame, text="Type:", font=self.font_medium_bold, text_color=self.text_color).pack(side="left")
            type_text = f"{invoice_type.title()}"
            if invoice_type == "dine in" and table_number:
                type_text += f" - Table {table_number}"
            ctk.CTkLabel(type_frame, text=type_text, font=self.font_medium, text_color=border_color).pack(side="left", padx=5)
            ctk.CTkFrame(type_frame, fg_color=self.text_color, height=1).pack(fill="x", pady=(5, 0))
            timestamp_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
            timestamp_frame.pack(fill="x", pady=(0, 5))
            ctk.CTkLabel(timestamp_frame, text="Timestamp:", font=self.font_medium_bold, text_color=self.text_color).pack(side="left")
            ctk.CTkLabel(timestamp_frame, text=timestamp, font=self.font_medium, text_color=self.text_color).pack(side="left", padx=5)
            ctk.CTkFrame(timestamp_frame, fg_color=self.text_color, height=1).pack(fill="x", pady=(5, 0))
            status_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
            status_frame.pack(fill="x", pady=(0, 10))
            ctk.CTkLabel(status_frame, text="Status:", font=self.font_medium_bold, text_color=self.text_color).pack(side="left")
            ctk.CTkLabel(status_frame, text=status, font=self.font_medium, text_color=self.text_color).pack(side="left", padx=5)
            ctk.CTkFrame(status_frame, fg_color=self.text_color, height=1).pack(fill="x", pady=(5, 0))
            scrollable_dish_frame = ctk.CTkScrollableFrame(
                self.details_frame,
                fg_color=(self.row_color_1, self.row_color_2),
                corner_radius=8,
                height=320
            )
            scrollable_dish_frame.pack(fill="both", expand=True, padx=20, pady=(10, 0))
            if items:
                header_frame = ctk.CTkFrame(scrollable_dish_frame, fg_color=self.primary_color, corner_radius=5)
                header_frame.pack(fill="x", pady=(5, 5))
                ctk.CTkLabel(header_frame, text="Dish Name", font=self.font_small_bold, text_color="white", width=180, anchor="w").pack(side="left", padx=5)
                ctk.CTkLabel(header_frame, text="Qty", font=self.font_small_bold, text_color="white", width=60, anchor="center").pack(side="left", padx=5)
                ctk.CTkLabel(header_frame, text="Total", font=self.font_small_bold, text_color="white", width=140, anchor="e").pack(side="left", padx=5)
                for idx, (dish_name, quantity, price) in enumerate(items):
                    total_price = quantity * price
                    row_color = self.row_color_1 if idx % 2 == 0 else self.row_color_2
                    dish_frame = ctk.CTkFrame(scrollable_dish_frame, fg_color=row_color, corner_radius=5)
                    dish_frame.pack(fill="x", pady=2)
                    ctk.CTkLabel(dish_frame, text=dish_name, font=self.font_small, width=180, anchor="w").pack(side="left", padx=5)
                    ctk.CTkLabel(dish_frame, text=str(quantity), font=self.font_small, width=60, anchor="center").pack(side="left", padx=5)
                    ctk.CTkLabel(dish_frame, text=f"${total_price:.2f}", font=self.font_small, width=140, anchor="e").pack(side="left", padx=5)
                    dish_frame.bind("<Enter>", lambda event, f=dish_frame: self.on_dish_row_enter(event, f))
                    dish_frame.bind("<Leave>", lambda event, f=dish_frame, c=row_color: self.on_dish_row_leave(event, f, c))
                    for child in dish_frame.winfo_children():
                        child.bind("<Enter>", lambda event, f=dish_frame: self.on_dish_row_enter(event, f))
                        child.bind("<Leave>", lambda event, f=dish_frame, c=row_color: self.on_dish_row_leave(event, f, c))
            else:
                ctk.CTkLabel(scrollable_dish_frame, text="No dishes in this invoice.", font=self.font_medium).pack(pady=10)
            separator = ctk.CTkFrame(self.details_frame, fg_color=self.text_color, height=2)
            separator.pack(fill="x", padx=20, pady=(10, 5))
            total_frame = ctk.CTkFrame(self.details_frame, fg_color="transparent", border_width=0)
            total_frame.pack(fill="x", padx=20, pady=(0, 10))
            ctk.CTkLabel(total_frame, text="Total Amount:", font=self.font_small, text_color=self.text_color, width=180, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(total_frame, text="", font=self.font_small, width=60, anchor="center").pack(side="left", padx=5)
            ctk.CTkLabel(total_frame, text=f"${total_amount:.2f}", font=self.font_small, text_color=self.price_green, width=140, anchor="e").pack(side="left", padx=5)
            pay_button = ctk.CTkButton(
                self.action_button_frame,
                text="Pay",
                command=lambda: self.pay_invoice(invoice_id, table_id, invoice_type),
                font=self.font_button,
                fg_color=(self.primary_color, self.primary_dark),
                text_color="white",
                width=425,
                height=40,
                corner_radius=10
            )
            pay_button.pack(fill="x", padx=20, pady=(10, 5))
            pay_button.bind("<Enter>", lambda event, b=pay_button: self.on_action_button_enter(event, b, self.primary_color, self.primary_dark))
            pay_button.bind("<Leave>", lambda event, b=pay_button: self.on_action_button_leave(event, b, self.primary_color, self.primary_dark))
            delete_print_frame = ctk.CTkFrame(self.action_button_frame, fg_color="transparent")
            delete_print_frame.pack(fill="x", padx=20, pady=(5, 10))
            delete_button = ctk.CTkButton(
                delete_print_frame,
                text="Delete Invoice",
                image=self.delete_icon,
                compound="left",
                command=lambda: self.delete_invoice(invoice_id, table_id, invoice_type),
                font=self.font_button,
                fg_color=(self.delete_color, self.delete_dark),
                text_color="white",
                width=187,
                height=40,
                corner_radius=10
            )
            delete_button.pack(side="left", padx=(0, 5))
            delete_button.bind("<Enter>", lambda event, b=delete_button: self.on_action_button_enter(event, b, self.delete_color, self.delete_dark))
            delete_button.bind("<Leave>", lambda event, b=delete_button: self.on_action_button_leave(event, b, self.delete_color, self.delete_dark))
            print_button = ctk.CTkButton(
                delete_print_frame,
                text="Print Invoice",
                image=self.print_icon,
                compound="left",
                command=lambda: self.print_invoice(invoice_id, invoice_type, table_number, timestamp, status, items, total_amount),
                font=self.font_button,
                fg_color=(self.print_color, self.print_dark),
                text_color="black",
                width=187,
                height=40,
                corner_radius=10
            )
            print_button.pack(side="left", padx=(5, 0))
            print_button.bind("<Enter>", lambda event, b=print_button: self.on_action_button_enter(event, b, self.print_color, self.print_dark))
            print_button.bind("<Leave>", lambda event, b=print_button: self.on_action_button_leave(event, b, self.print_color, self.print_dark))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load invoice details: {e}")

    def show_add_invoice(self):
        try:
            from add_invoice_screen import AddInvoiceScreen
            for widget in self.root.winfo_children():
                widget.destroy()
            AddInvoiceScreen(self.root, self.role)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Add Invoice screen: {e}")

    def show_edit_invoice(self, invoice_id):
        try:
            for widget in self.root.winfo_children():
                widget.destroy()
            EditInvoiceScreen(self.root, self.role, invoice_id)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Edit Invoice screen: {e}")

    def show_manage_staffs(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        ManageStaffs(self.root, self.role)

    def show_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        MenuScreen(self.root, self.role)

    def show_table_management(self):
        try:
            from table_management_screen import TableManagementScreen
            for widget in self.root.winfo_children():
                widget.destroy()
            TableManagementScreen(self.root, self.role)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Table Management screen: {e}")

    def show_paid_invoices(self):
        try:
            for widget in self.root.winfo_children():
                widget.destroy()
            PaidInvoicesScreen(self.root, self.role)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Paid Invoices screen: {e}")

    def logout(self):
        from login_screen import LoginScreen
        for widget in self.root.winfo_children():
            widget.destroy()
        LoginScreen(self.root)

    def print_invoice(self, invoice_id, invoice_type, table_number, timestamp, status, items, total_amount):
        try:
            invoices_folder = "invoices"
            if not os.path.exists(invoices_folder):
                os.makedirs(invoices_folder)
            pdf_filename = os.path.join(invoices_folder, f"invoice_{invoice_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            c = canvas.Canvas(pdf_filename, pagesize=letter)
            width, height = letter
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "Restaurant Invoice")
            c.setFont("Helvetica", 12)
            c.drawString(50, height - 80, f"Invoice #{invoice_id}")
            c.drawString(50, height - 100, f"Type: {invoice_type.title()}{' - Table ' + str(table_number) if invoice_type == 'dine in' and table_number else ''}")
            c.drawString(50, height - 120, f"Timestamp: {timestamp}")
            c.drawString(50, height - 140, f"Status: {status}")
            y_position = height - 180
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y_position, "Dish Name")
            c.drawString(300, y_position, "Qty")
            c.drawString(400, y_position, "Total")
            c.line(50, y_position - 5, width - 50, y_position - 5)
            y_position -= 30
            c.setFont("Helvetica", 12)
            for dish_name, quantity, price in items:
                total_price = quantity * price
                c.drawString(50, y_position, dish_name)
                c.drawString(300, y_position, str(quantity))
                c.drawString(400, y_position, f"${total_price:.2f}")
                y_position -= 20
                if y_position < 50:
                    c.showPage()
                    y_position = height - 50
                    c.setFont("Helvetica", 12)
            y_position -= 20
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y_position, f"Total Amount: ${total_amount:.2f}")
            c.save()
            messagebox.showinfo("Success", f"Invoice #{invoice_id} has been saved as a PDF in the 'invoices' folder.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save invoice as PDF: {e}")

    def process_payment(self, invoice_id, table_id, invoice_type, payment_type, dialog):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
            invoice = cursor.fetchone()
            if not invoice:
                conn.close()
                raise Exception(f"Invoice with ID {invoice_id} not found.")
            cursor.execute('''
                INSERT INTO paid_invoices (table_id, total_amount, timestamp, type, status, invoice_id, payment_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (invoice[1], invoice[2], invoice[3], invoice[4], 'paid', invoice_id, payment_type))
            cursor.execute("UPDATE invoices SET status = 'paid' WHERE id = ?", (invoice_id,))
            if invoice_type == "dine in" and table_id:
                update_table_status(table_id, conn)
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Invoice #{invoice_id} has been marked as paid with {payment_type}.")
            dialog.destroy()
            self.load_invoices()
            for widget in self.details_frame.winfo_children():
                widget.destroy()
            self.details_label = ctk.CTkLabel(self.details_frame, text="Invoice Details", font=self.font_header, text_color=self.header_color)
            self.details_label.pack(pady=20)
            for widget in self.action_button_frame.winfo_children():
                widget.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to pay invoice: {e}")
            if 'conn' in locals():
                conn.close()

    def pay_invoice(self, invoice_id, table_id, invoice_type):
        self.show_payment_dialog(invoice_id, table_id, invoice_type)

    def delete_invoice(self, invoice_id, table_id, invoice_type):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
            cursor.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
            if invoice_type == "dine in" and table_id:
                cursor.execute("SELECT COUNT(*) FROM invoices WHERE table_id = ? AND type = 'dine in' AND status = 'unpaid'", (table_id,))
                unpaid_count = cursor.fetchone()[0]
                if unpaid_count == 0:
                    cursor.execute("UPDATE tables SET status = 'empty' WHERE id = ?", (table_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Invoice #{invoice_id} has been deleted.")
            self.load_invoices()
            for widget in self.details_frame.winfo_children():
                widget.destroy()
            self.details_label = ctk.CTkLabel(self.details_frame, text="Invoice Details", font=self.font_header, text_color=self.header_color)
            self.details_label.pack(pady=20)
            for widget in self.action_button_frame.winfo_children():
                widget.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete invoice: {e}")
            if 'conn' in locals():
                conn.close()

    def show_payment_dialog(self, invoice_id, table_id, invoice_type):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Select Payment Type")
        dialog_width = 950
        dialog_height = 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_position = (screen_width - dialog_width) // 2
        y_position = (screen_height - dialog_height) // 2
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x_position}+{y_position}")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(fg_color=("white", self.background_start))
        ctk.CTkLabel(
            dialog,
            text="Choose Payment Type",
            font=self.font_dialog_title,
            text_color=(self.dark_gray, self.header_color)
        ).pack(pady=(30, 20))
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=10)
        button_frame.pack_propagate(False)
        max_text_length = max(len("Cash"), len("Bank Transfer"), len("VISA Card"))
        padded_cash_text = "Cash".center(max_text_length)
        padded_bank_text = "Bank Transfer".center(max_text_length)
        padded_card_text = "VISA Card".center(max_text_length)
        cash_button = ctk.CTkButton(
            button_frame,
            text=padded_cash_text,
            image=self.payment_icons.get("cash.png"),
            compound="left",
            font=self.font_payment_button,
            fg_color=(self.primary_color, self.primary_dark),
            text_color="white",
            width=300,
            height=100,
            corner_radius=10,
            border_width=2,
            border_color="gray50",
            command=lambda: self.process_payment(invoice_id, table_id, invoice_type, "Cash", dialog)
        )
        cash_button.pack(side="left", padx=10)
        cash_button.pack_propagate(False)
        cash_button.bind("<Enter>", lambda event, b=cash_button: self.on_payment_button_enter(event, b, self.primary_color, self.primary_dark))
        cash_button.bind("<Leave>", lambda event, b=cash_button: self.on_payment_button_leave(event, b, self.primary_color, self.primary_dark))
        dialog.update()
        bank_button = ctk.CTkButton(
            button_frame,
            text=padded_bank_text,
            image=self.payment_icons.get("bank.png"),
            compound="left",
            font=self.font_payment_button,
            fg_color=(self.bank_color, self.bank_dark),
            text_color="white",
            width=300,
            height=100,
            corner_radius=10,
            border_width=2,
            border_color="gray50",
            command=lambda: self.process_payment(invoice_id, table_id, invoice_type, "Bank Transfer", dialog)
        )
        bank_button.pack(side="left", padx=10)
        bank_button.pack_propagate(False)
        bank_button.bind("<Enter>", lambda event, b=bank_button: self.on_payment_button_enter(event, b, self.bank_color, self.bank_dark))
        bank_button.bind("<Leave>", lambda event, b=bank_button: self.on_payment_button_leave(event, b, self.bank_color, self.bank_dark))
        dialog.update()
        card_button = ctk.CTkButton(
            button_frame,
            text=padded_card_text,
            image=self.payment_icons.get("card.png"),
            compound="left",
            font=self.font_payment_button,
            fg_color=(self.card_color, self.card_dark),
            text_color="white",
            width=300,
            height=100,
            corner_radius=10,
            border_width=2,
            border_color="gray50",
            command=lambda: self.process_payment(invoice_id, table_id, invoice_type, "VISA Card", dialog)
        )
        card_button.pack(side="left", padx=10)
        card_button.pack_propagate(False)
        card_button.bind("<Enter>", lambda event, b=card_button: self.on_payment_button_enter(event, b, self.card_color, self.card_dark))
        card_button.bind("<Leave>", lambda event, b=card_button: self.on_payment_button_leave(event, b, self.card_color, self.card_dark))
        dialog.update()
        cancel_button = ctk.CTkButton(
            dialog,
            text="Cancel",
            font=self.font_payment_button,
            fg_color=(self.delete_color, self.delete_dark),
            text_color="white",
            width=200,
            height=40,
            corner_radius=10,
            command=dialog.destroy
        )
        cancel_button.pack(pady=(20, 30))
        cancel_button.bind("<Enter>", lambda event, b=cancel_button: self.on_action_button_enter(event, b, self.delete_color, self.delete_dark))
        cancel_button.bind("<Leave>", lambda event, b=cancel_button: self.on_action_button_leave(event, b, self.delete_color, self.delete_dark))