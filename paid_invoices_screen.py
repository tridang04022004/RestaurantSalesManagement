import customtkinter as ctk
from tkinter import messagebox
from db_connection import get_db_connection
import os
import platform
import subprocess
import glob

class PaidInvoicesScreen:
    def __init__(self, root, role):
        self.root = root
        self.role = role
        self.root.title(f"Paid Invoices - {role.capitalize()}")
        window_width = 1600
        window_height = 900
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.primary_color = "#9ACBD0"
        self.primary_dark = "#006A71"
        self.accent_color = "#F4A261"
        self.accent_dark = "#E77B2B"
        self.background_start = "#F2EFE7"
        self.background_end = "#E8E4D9"
        self.text_color = "#48A6A7"
        self.header_color = "#006A71"
        self.total_amount_color = "#D4A017"  # Gold for Total Amount
        self.type_deliver_color = "#A100A1"  # Purple for Deliver
        self.type_takeaway_color = "#F4A261"  # Orange for Takeaway (matches accent color)
        self.type_dinein_color = "#006A71"  # Blue for Dine-in (matches header color)
        self.shadow_color = "#D3CFC3"
        self.row_color_1 = "#F9F7F0"
        self.row_color_2 = "#EDEBE3"
        self.hover_color = "#D1E8E8"
        self.font_title = ("Helvetica", 24, "bold")
        self.font_header = ("Helvetica", 16, "bold")
        self.font_body = ("Helvetica", 14)
        self.font_button = ("Helvetica", 14, "bold")
        self.show_paid_invoices()

    def darken_color(self, hex_color):
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = max(0, int(r * 0.8))
        g = max(0, int(g * 0.8))
        b = max(0, int(b * 0.8))
        return f"#{r:02x}{g:02x}{b:02x}"

    def on_row_enter(self, event, frame):
        frame.configure(fg_color=self.hover_color)

    def on_row_leave(self, event, frame, original_color):
        frame.configure(fg_color=original_color)

    def on_action_button_enter(self, event, button, original_gradient_start, original_gradient_end):
        darkened_start = self.darken_color(original_gradient_start)
        darkened_end = self.darken_color(original_gradient_end)
        button.configure(fg_color=(darkened_start, darkened_end))

    def on_action_button_leave(self, event, button, original_gradient_start, original_gradient_end):
        button.configure(fg_color=(original_gradient_start, original_gradient_end))

    def print_paid_invoice(self, invoice_id):
        try:
            invoices_folder = "invoices"
            pdf_pattern = os.path.join(invoices_folder, f"invoice_{invoice_id}_*.pdf")
            pdf_files = glob.glob(pdf_pattern)
            if not pdf_files:
                messagebox.showerror("Error", f"No PDF found for Invoice #{invoice_id} in the 'invoices' folder.")
                return
            pdf_files.sort(key=os.path.getmtime, reverse=True)
            pdf_filename = pdf_files[0]
            if platform.system() == "Windows":
                os.startfile(pdf_filename, "print")
            elif platform.system() == "Darwin":
                subprocess.run(["open", pdf_filename])
            else:
                subprocess.run(["xdg-open", pdf_filename])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print invoice: {e}")

    def show_paid_invoices(self):
        main_frame = ctk.CTkFrame(self.root, fg_color=(self.background_start, self.background_end))
        main_frame.pack(fill="both", expand=True)
        top_bar = ctk.CTkFrame(main_frame, fg_color="transparent", height=60)
        top_bar.pack(fill="x", padx=20, pady=(10, 0))
        back_button = ctk.CTkButton(
            top_bar,
            text="← Back",
            font=self.font_button,
            fg_color=(self.primary_color, self.primary_dark),
            text_color="white",
            width=120,
            height=40,
            corner_radius=10,
            command=self.show_main_screen
        )
        back_button.pack(side="left")
        back_button.bind("<Enter>", lambda event, b=back_button: self.on_action_button_enter(event, b, self.primary_color, self.primary_dark))
        back_button.bind("<Leave>", lambda event, b=back_button: self.on_action_button_leave(event, b, self.primary_color, self.primary_dark))
        ctk.CTkLabel(
            top_bar,
            text="Paid Invoices",
            font=self.font_title,
            text_color=self.header_color
        ).pack(side="left", padx=20)
        main_panel = ctk.CTkFrame(main_frame, fg_color="transparent")
        main_panel.pack(fill="both", expand=True, padx=20, pady=20)
        table_container = ctk.CTkFrame(
            main_panel,
            fg_color="white",
            corner_radius=15,
            border_width=2,
            border_color=self.shadow_color
        )
        table_container.pack(fill="both", expand=True, padx=50, pady=20)
        self.scrollable_frame = ctk.CTkScrollableFrame(
            table_container,
            fg_color="transparent",
            width=1420,
            height=550,
            corner_radius=10
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
        header_frame = ctk.CTkFrame(self.scrollable_frame, fg_color=self.header_color, corner_radius=10)
        header_frame.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(header_frame, text="Invoice ID", font=self.font_header, text_color="white", width=120, anchor="center").pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Table Number", font=self.font_header, text_color="white", width=120, anchor="center").pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Total Amount", font=self.font_header, text_color="white", width=180, anchor="center").pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Type", font=self.font_header, text_color="white", width=180, anchor="center").pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Timestamp", font=self.font_header, text_color="white", width=300, anchor="center").pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Status", font=self.font_header, text_color="white", width=120, anchor="center").pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Payment Type", font=self.font_header, text_color="white", width=180, anchor="center").pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Action", font=self.font_header, text_color="white", width=140, anchor="center").pack(side="left", padx=5)
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT pi.invoice_id, t.table_number, pi.total_amount, pi.type, pi.timestamp, pi.status, pi.payment_type
                FROM paid_invoices pi
                LEFT JOIN tables t ON pi.table_id = t.id
            ''')
            paid_invoices = cursor.fetchall()
            conn.close()
            for idx, (invoice_id, table_number, total_amount, invoice_type, timestamp, status, payment_type) in enumerate(paid_invoices):
                row_color = self.row_color_1 if idx % 2 == 0 else self.row_color_2
                row_frame = ctk.CTkFrame(
                    self.scrollable_frame,
                    fg_color=row_color,
                    corner_radius=8,
                    border_width=1,
                    border_color="#E0E0E0"
                )
                row_frame.pack(fill="x", pady=4, padx=5)
                ctk.CTkLabel(row_frame, text=str(invoice_id), font=self.font_body, text_color=self.text_color, width=120, anchor="center").pack(side="left", padx=5, pady=8)
                ctk.CTkLabel(row_frame, text=str(table_number) if table_number else "N/A", font=self.font_body, text_color=self.text_color, width=120, anchor="center").pack(side="left", padx=5, pady=8)
                ctk.CTkLabel(row_frame, text=f"${total_amount:.2f}", font=self.font_body, text_color=self.total_amount_color, width=180, anchor="center").pack(side="left", padx=5, pady=8)
                # Determine the color for the Type column based on the invoice type
                type_color = self.text_color  # Default color
                if invoice_type.lower() == "delivery":
                    type_color = self.type_deliver_color
                elif invoice_type.lower() == "take away":
                    type_color = self.type_takeaway_color
                elif invoice_type.lower() == "dine in":
                    type_color = self.type_dinein_color
                ctk.CTkLabel(row_frame, text=invoice_type.title(), font=self.font_body, text_color=type_color, width=180, anchor="center").pack(side="left", padx=5, pady=8)
                ctk.CTkLabel(row_frame, text=timestamp, font=self.font_body, text_color=self.text_color, width=300, anchor="center").pack(side="left", padx=5, pady=8)
                ctk.CTkLabel(row_frame, text=status, font=self.font_body, text_color=self.text_color, width=120, anchor="center").pack(side="left", padx=5, pady=8)
                ctk.CTkLabel(row_frame, text=payment_type, font=self.font_body, text_color=self.text_color, width=180, anchor="center").pack(side="left", padx=5, pady=8)
                print_button = ctk.CTkButton(
                    row_frame,
                    text="Print",
                    command=lambda inv_id=invoice_id: self.print_paid_invoice(inv_id),
                    font=self.font_body,
                    fg_color=(self.accent_color, self.accent_dark),
                    text_color="white",
                    width=100,
                    height=40,
                    corner_radius=8,
                    border_width=1,
                    border_color=self.accent_dark
                )
                print_button.pack(side="left", padx=5, pady=8)
                print_button.bind("<Enter>", lambda event, b=print_button: self.on_action_button_enter(event, b, self.accent_color, self.accent_dark))
                print_button.bind("<Leave>", lambda event, b=print_button: self.on_action_button_leave(event, b, self.accent_color, self.accent_dark))
                row_frame.bind("<Enter>", lambda event, f=row_frame: self.on_row_enter(event, f))
                row_frame.bind("<Leave>", lambda event, f=row_frame, c=row_color: self.on_row_leave(event, f, c))
                for child in row_frame.winfo_children():
                    child.bind("<Enter>", lambda event, f=row_frame: self.on_row_enter(event, f))
                    child.bind("<Leave>", lambda event, f=row_frame, c=row_color: self.on_row_leave(event, f, c))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load paid invoices: {e}")

    def show_main_screen(self):
        from main_screen import MainScreen
        for widget in self.root.winfo_children():
            widget.destroy()
        MainScreen(self.root, self.role)