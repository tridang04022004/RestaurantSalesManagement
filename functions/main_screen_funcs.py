import customtkinter as ctk
from tkinter import messagebox
from db_connection import get_db_connection, update_table_status
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import datetime

def load_invoices(invoices_frame, root, row_color_1, row_color_2, primary_color, primary_dark, background_start, background_end,
                 dine_in_color, take_away_color, delivery_color, dark_gray, price_green, font_id, font_type, font_price,
                 edit_icon, on_invoice_enter, on_invoice_leave, on_edit_enter, on_edit_leave, display_invoice_callback, show_edit_invoice):
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
        for widget in invoices_frame.winfo_children():
            widget.destroy()
        num_rows = (len(invoices) + 2) // 3
        required_height = num_rows * 240
        invoices_frame.configure(height=required_height)
        for idx, (invoice_id, table_id, total_amount, invoice_type, table_number) in enumerate(invoices):
            row = idx // 3
            col = idx % 3
            border_color = dine_in_color if invoice_type == "dine in" else \
                          take_away_color if invoice_type == "take away" else \
                          delivery_color
            invoice_frame = ctk.CTkFrame(
                invoices_frame,
                fg_color=(background_start, background_end),
                width=200,
                height=200,
                border_width=2,
                border_color=border_color,
                corner_radius=12
            )
            invoice_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            invoice_frame.grid_propagate(False)
            invoice_frame.bind("<Enter>", lambda event, f=invoice_frame, bc=border_color, bg=background_start: on_invoice_enter(event, f, bc, bg))
            invoice_frame.bind("<Leave>", lambda event, f=invoice_frame, bc=border_color, bg=background_start: on_invoice_leave(event, f, bc, bg))
            invoice_frame.bind("<Button-1>", lambda event, inv_id=invoice_id: display_invoice_callback(inv_id))
            id_label = ctk.CTkLabel(
                invoice_frame,
                text=f"#{invoice_id}",
                font=font_id,
                text_color=dark_gray,
                fg_color=(row_color_1, row_color_2),
                corner_radius=5,
                padx=5,
                pady=2
            )
            id_label.pack(pady=(20, 0))
            id_label.bind("<Button-1>", lambda event, inv_id=invoice_id: display_invoice_callback(inv_id))
            display_type = f"{invoice_type.title()} - Table {table_number}" if invoice_type == "dine in" and table_number else invoice_type.title()
            type_frame = ctk.CTkFrame(invoice_frame, fg_color="transparent")
            type_frame.pack(pady=(10, 0))
            type_label = ctk.CTkLabel(
                type_frame,
                text=display_type,
                font=font_type,
                text_color=border_color
            )
            type_label.pack()
            underline = ctk.CTkFrame(type_frame, fg_color=border_color, height=2)
            underline.pack(fill="x", padx=5)
            type_label.bind("<Button-1>", lambda event, inv_id=invoice_id: display_invoice_callback(inv_id))
            underline.bind("<Button-1>", lambda event, inv_id=invoice_id: display_invoice_callback(inv_id))
            price_label = ctk.CTkLabel(
                invoice_frame,
                text=f"Total Price: ${total_amount:.2f}",
                font=font_price,
                text_color=price_green,
                fg_color=(row_color_1, row_color_2),
                corner_radius=5,
                padx=5,
                pady=2
            )
            price_label.pack(pady=(20, 0))
            price_label.bind("<Button-1>", lambda event, inv_id=invoice_id: display_invoice_callback(inv_id))
            edit_button = ctk.CTkButton(
                master=invoice_frame,
                text="" if edit_icon else "Edit",
                image=edit_icon,
                command=lambda inv_id=invoice_id: show_edit_invoice(inv_id),
                width=40,
                height=40,
                fg_color=primary_color,
                corner_radius=10
            )
            edit_button.pack(pady=(10, 10))
            edit_button.bind("<Enter>", lambda event, b=edit_button: on_edit_enter(event, b))
            edit_button.bind("<Leave>", lambda event, b=edit_button: on_edit_leave(event, b))
        for i in range((len(invoices) + 2) // 3):
            invoices_frame.grid_rowconfigure(i, weight=1, minsize=240)
        for j in range(3):
            invoices_frame.grid_columnconfigure(j, weight=1, minsize=220)
        invoices_frame.grid_propagate(False)
        root.update()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load invoices: {e}")

def display_invoice_details(invoice_id, details_frame, action_button_frame, header_color, row_color_1, row_color_2,
                           primary_color, primary_dark, text_color, dine_in_color, take_away_color, delivery_color,
                           font_header, font_medium_bold, font_medium, font_small_bold, font_small, price_green,
                           on_dish_row_enter, on_dish_row_leave, pay_invoice_callback, delete_invoice_callback, print_invoice_callback,
                           delete_icon, print_icon, delete_color, delete_dark, print_color, print_dark,
                           on_action_button_enter, on_action_button_leave):
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
        for widget in details_frame.winfo_children():
            widget.destroy()
        for widget in action_button_frame.winfo_children():
            widget.destroy()
        border_color = dine_in_color if invoice_type == "dine in" else \
                      take_away_color if invoice_type == "take away" else \
                      delivery_color
        id_label = ctk.CTkLabel(
            details_frame,
            text=f"Invoice #{invoice_id}",
            font=("Helvetica", 24, "bold"),
            text_color=(header_color, border_color),
            fg_color=(row_color_1, row_color_2),
            corner_radius=8,
            padx=10,
            pady=5
        )
        id_label.pack(pady=(10, 15))
        details_frame_inner = ctk.CTkFrame(details_frame, fg_color="transparent")
        details_frame_inner.pack(fill="x", padx=20)
        type_frame = ctk.CTkFrame(details_frame_inner, fg_color="transparent")
        type_frame.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(type_frame, text="Type:", font=font_medium_bold, text_color=text_color).pack(side="left")
        type_text = f"{invoice_type.title()}"
        if invoice_type == "dine in" and table_number:
            type_text += f" - Table {table_number}"
        ctk.CTkLabel(type_frame, text=type_text, font=font_medium, text_color=border_color).pack(side="left", padx=5)
        ctk.CTkFrame(type_frame, fg_color=text_color, height=1).pack(fill="x", pady=(5, 0))
        timestamp_frame = ctk.CTkFrame(details_frame_inner, fg_color="transparent")
        timestamp_frame.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(timestamp_frame, text="Timestamp:", font=font_medium_bold, text_color=text_color).pack(side="left")
        ctk.CTkLabel(timestamp_frame, text=timestamp, font=font_medium, text_color=text_color).pack(side="left", padx=5)
        ctk.CTkFrame(timestamp_frame, fg_color=text_color, height=1).pack(fill="x", pady=(5, 0))
        status_frame = ctk.CTkFrame(details_frame_inner, fg_color="transparent")
        status_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(status_frame, text="Status:", font=font_medium_bold, text_color=text_color).pack(side="left")
        ctk.CTkLabel(status_frame, text=status, font=font_medium, text_color=text_color).pack(side="left", padx=5)
        ctk.CTkFrame(status_frame, fg_color=text_color, height=1).pack(fill="x", pady=(5, 0))
        scrollable_dish_frame = ctk.CTkScrollableFrame(
            details_frame,
            fg_color=(row_color_1, row_color_2),
            corner_radius=8,
            height=320
        )
        scrollable_dish_frame.pack(fill="both", expand=True, padx=20, pady=(10, 0))
        if items:
            header_frame = ctk.CTkFrame(scrollable_dish_frame, fg_color=primary_color, corner_radius=5)
            header_frame.pack(fill="x", pady=(5, 5))
            ctk.CTkLabel(header_frame, text="Dish Name", font=font_small_bold, text_color="white", width=180, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(header_frame, text="Qty", font=font_small_bold, text_color="white", width=60, anchor="center").pack(side="left", padx=5)
            ctk.CTkLabel(header_frame, text="Total", font=font_small_bold, text_color="white", width=140, anchor="e").pack(side="left", padx=5)
            for idx, (dish_name, quantity, price) in enumerate(items):
                total_price = quantity * price
                row_color = row_color_1 if idx % 2 == 0 else row_color_2
                dish_frame = ctk.CTkFrame(scrollable_dish_frame, fg_color=row_color, corner_radius=5)
                dish_frame.pack(fill="x", pady=2)
                ctk.CTkLabel(dish_frame, text=dish_name, font=font_small, width=180, anchor="w").pack(side="left", padx=5)
                ctk.CTkLabel(dish_frame, text=str(quantity), font=font_small, width=60, anchor="center").pack(side="left", padx=5)
                ctk.CTkLabel(dish_frame, text=f"${total_price:.2f}", font=font_small, width=140, anchor="e").pack(side="left", padx=5)
                dish_frame.bind("<Enter>", lambda event, f=dish_frame: on_dish_row_enter(event, f))
                dish_frame.bind("<Leave>", lambda event, f=dish_frame, c=row_color: on_dish_row_leave(event, f, c))
                for child in dish_frame.winfo_children():
                    child.bind("<Enter>", lambda event, f=dish_frame: on_dish_row_enter(event, f))
                    child.bind("<Leave>", lambda event, f=dish_frame, c=row_color: on_dish_row_leave(event, f, c))
        else:
            ctk.CTkLabel(scrollable_dish_frame, text="No dishes in this invoice.", font=font_medium).pack(pady=10)
        separator = ctk.CTkFrame(details_frame, fg_color=text_color, height=2)
        separator.pack(fill="x", padx=20, pady=(10, 5))
        total_frame = ctk.CTkFrame(details_frame, fg_color="transparent", border_width=0)
        total_frame.pack(fill="x", padx=20, pady=(0, 10))
        ctk.CTkLabel(total_frame, text="Total Amount:", font=font_small, text_color=text_color, width=180, anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(total_frame, text="", font=font_small, width=60, anchor="center").pack(side="left", padx=5)
        ctk.CTkLabel(total_frame, text=f"${total_amount:.2f}", font=font_small, text_color=price_green, width=140, anchor="e").pack(side="left", padx=5)
        pay_button = ctk.CTkButton(
            action_button_frame,
            text="Pay",
            command=lambda: pay_invoice_callback(invoice_id, table_id, invoice_type),
            font=font_small_bold,
            fg_color=(primary_color, primary_dark),
            text_color="white",
            width=425,
            height=40,
            corner_radius=10
        )
        pay_button.pack(fill="x", padx=20, pady=(10, 5))
        pay_button.bind("<Enter>", lambda event, b=pay_button: on_action_button_enter(event, b, primary_color, primary_dark))
        pay_button.bind("<Leave>", lambda event, b=pay_button: on_action_button_leave(event, b, primary_color, primary_dark))
        delete_print_frame = ctk.CTkFrame(action_button_frame, fg_color="transparent")
        delete_print_frame.pack(fill="x", padx=20, pady=(5, 10))
        delete_button = ctk.CTkButton(
            delete_print_frame,
            text="Delete Invoice",
            image=delete_icon,
            compound="left",
            command=lambda: delete_invoice_callback(invoice_id, table_id, invoice_type),
            font=font_small_bold,
            fg_color=(delete_color, delete_dark),
            text_color="white",
            width=187,
            height=40,
            corner_radius=10
        )
        delete_button.pack(side="left", padx=(0, 5))
        delete_button.bind("<Enter>", lambda event, b=delete_button: on_action_button_enter(event, b, delete_color, delete_dark))
        delete_button.bind("<Leave>", lambda event, b=delete_button: on_action_button_leave(event, b, delete_color, delete_dark))
        print_button = ctk.CTkButton(
            delete_print_frame,
            text="Print Invoice",
            image=print_icon,
            compound="left",
            command=lambda: print_invoice_callback(invoice_id, invoice_type, table_number, timestamp, status, items, total_amount),
            font=font_small_bold,
            fg_color=(print_color, print_dark),
            text_color="black",
            width=187,
            height=40,
            corner_radius=10
        )
        print_button.pack(side="left", padx=(5, 0))
        print_button.bind("<Enter>", lambda event, b=print_button: on_action_button_enter(event, b, print_color, print_dark))
        print_button.bind("<Leave>", lambda event, b=print_button: on_action_button_leave(event, b, print_color, print_dark))
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load invoice details: {e}")

def print_invoice(invoice_id, invoice_type, table_number, timestamp, status, items, total_amount):
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

def process_payment(invoice_id, table_id, invoice_type, payment_type, dialog, load_invoices_callback, details_frame, 
                    action_button_frame, header_color, font_header):
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
        load_invoices_callback()
        for widget in details_frame.winfo_children():
            widget.destroy()
        details_label = ctk.CTkLabel(details_frame, text="Invoice Details", font=font_header, text_color=header_color)
        details_label.pack(pady=20)
        for widget in action_button_frame.winfo_children():
            widget.destroy()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to pay invoice: {e}")
        if 'conn' in locals():
            conn.close()

def pay_invoice(invoice_id, table_id, invoice_type, show_payment_dialog):
    show_payment_dialog(invoice_id, table_id, invoice_type)

def delete_invoice(invoice_id, table_id, invoice_type, load_invoices_callback, details_frame, action_button_frame, 
                   header_color, font_header):
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
        load_invoices_callback()
        for widget in details_frame.winfo_children():
            widget.destroy()
        details_label = ctk.CTkLabel(details_frame, text="Invoice Details", font=font_header, text_color=header_color)
        details_label.pack(pady=20)
        for widget in action_button_frame.winfo_children():
            widget.destroy()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to delete invoice: {e}")
        if 'conn' in locals():
            conn.close()