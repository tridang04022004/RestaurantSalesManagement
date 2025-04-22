import customtkinter as ctk
from tkinter import messagebox
import os

class TableManagementScreen:
    def __init__(self, root, role):
        self.root = root
        self.role = role
        self.root.title("Restaurant Management - Table Management")
        window_width = 1600
        window_height = 900
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.primary_color = "#9ACBD0"
        self.primary_dark = "#006A71"
        self.delete_color = "#FF6F61"
        self.delete_dark = "#D94F43"
        self.background_start = "#F2EFE7"
        self.background_end = "#E8E4D9"
        self.text_color = "#48A6A7"
        self.header_color = "#006A71"
        self.shadow_color = "#D3CFC3"
        self.status_empty = "#48A6A7"
        self.status_reserved = "#FF6F61"
        self.status_in_use = "#F4A261"
        self.font_title = ("Helvetica", 24, "bold")
        self.font_subtitle = ("Helvetica", 16, "bold")
        self.font_button = ("Helvetica", 14, "bold")
        self.font_table = ("Helvetica", 16)
        self.font_status = ("Helvetica", 14)
        self.edit_icon = None
        self.remove_icon = None
        try:
            edit_icon_path = os.path.join("icons", "edit.png")
            remove_icon_path = os.path.join("icons", "remove.png")
            if not os.path.exists(edit_icon_path):
                raise FileNotFoundError
            if not os.path.exists(remove_icon_path):
                raise FileNotFoundError
            from PIL import Image
            edit_icon = Image.open(edit_icon_path)
            remove_icon = Image.open(remove_icon_path)
            edit_icon = edit_icon.resize((30, 30), Image.Resampling.LANCZOS)
            remove_icon = remove_icon.resize((30, 30), Image.Resampling.LANCZOS)
            self.edit_icon = ctk.CTkImage(light_image=edit_icon, dark_image=edit_icon, size=(30, 30))
            self.remove_icon = ctk.CTkImage(light_image=remove_icon, dark_image=remove_icon, size=(30, 30))
        except Exception as e:
            self.edit_icon = None
            self.remove_icon = None
        self.all_tables = []
        try:
            self.show_tables()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Table Management screen: {e}")

    def darken_color(self, hex_color):
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = max(0, int(r * 0.8))
        g = max(0, int(g * 0.8))
        b = max(0, int(b * 0.8))
        return f"#{r:02x}{g:02x}{b:02x}"

    def on_table_frame_enter(self, event, frame):
        frame.configure(fg_color="#D1E8E8")

    def on_table_frame_leave(self, event, frame):
        frame.configure(fg_color="#F9F7F0")

    def on_action_button_enter(self, event, button, original_gradient_start, original_gradient_end):
        darkened_start = self.darken_color(original_gradient_start)
        darkened_end = self.darken_color(original_gradient_end)
        button.configure(fg_color=(darkened_start, darkened_end))

    def on_action_button_leave(self, event, button, original_gradient_start, original_gradient_end):
        button.configure(fg_color=(original_gradient_start, original_gradient_end))

    def show_tables(self):
        for widget in self.root.winfo_children():
            widget.destroy()
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
            command=self.back_to_main
        )
        back_button.pack(side="left")
        back_button.bind("<Enter>", lambda event, b=back_button: self.on_action_button_enter(event, b, self.primary_color, self.primary_dark))
        back_button.bind("<Leave>", lambda event, b=back_button: self.on_action_button_leave(event, b, self.primary_color, self.primary_dark))
        ctk.CTkLabel(
            top_bar,
            text="Table Management",
            font=self.font_title,
            text_color=self.header_color
        ).pack(side="left", padx=20)
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.scrollable_frame = ctk.CTkScrollableFrame(content_frame, fg_color="transparent", width=1200)
        self.scrollable_frame.pack(side="left", fill="both", expand=True)
        self.tables_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.tables_frame.pack(fill="both", expand=True)
        if not self.all_tables:
            try:
                from db_connection import get_all_tables
                self.all_tables = get_all_tables()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch tables: {e}")
                return
        self.display_tables()
        button_frame = ctk.CTkFrame(
            content_frame,
            fg_color="white",
            width=300,
            corner_radius=20,
            border_width=2,
            border_color=self.shadow_color
        )
        button_frame.pack(side="right", fill="y", padx=20, pady=20)
        button_frame.pack_propagate(False)
        add_button = ctk.CTkButton(
            button_frame,
            text="Add New Table",
            command=self.show_add_table_popup,
            font=self.font_button,
            width=200,
            height=50,
            fg_color=(self.primary_color, self.primary_dark),
            text_color="white",
            corner_radius=10,
            border_width=2,
            border_color=self.primary_dark
        )
        add_button.pack(pady=20)
        add_button.bind("<Enter>", lambda event, b=add_button: self.on_action_button_enter(event, b, self.primary_color, self.primary_dark))
        add_button.bind("<Leave>", lambda event, b=add_button: self.on_action_button_leave(event, b, self.primary_color, self.primary_dark))

    def display_tables(self):
        for widget in self.tables_frame.winfo_children():
            widget.destroy()
        num_columns = 3
        num_rows = (len(self.all_tables) + num_columns - 1) // num_columns
        required_height = num_rows * 190
        self.tables_frame.configure(height=required_height)
        table_frames = []
        for idx, (table_id, table_number, status) in enumerate(self.all_tables):
            row = idx // num_columns
            col = idx % num_columns
            table_frame = ctk.CTkFrame(
                self.tables_frame,
                fg_color="#F9F7F0",
                width=300,
                height=150,
                corner_radius=20,
                border_width=2,
                border_color=self.shadow_color
            )
            table_frame.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")
            table_frame.grid_propagate(False)
            table_frame.bind("<Enter>", lambda event, f=table_frame: self.on_table_frame_enter(event, f))
            table_frame.bind("<Leave>", lambda event, f=table_frame: self.on_table_frame_leave(event, f))
            table_frames.append((table_number, table_frame))
            name_label = ctk.CTkLabel(table_frame, text=f"TABLE {table_number}", font=self.font_table, text_color=self.text_color)
            name_label.pack(pady=(15, 0))
            status_color = self.status_empty if status == "empty" else self.status_reserved if status == "reserved" else self.status_in_use
            status_label = ctk.CTkLabel(table_frame, text=status, font=self.font_status, text_color=status_color)
            status_label.pack(pady=(5, 0))
            button_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
            button_frame.pack(pady=(5, 0))
            edit_button = ctk.CTkButton(
                master=button_frame,
                text="" if self.edit_icon else "Edit",
                image=self.edit_icon,
                command=lambda tid=table_id, tnum=table_number, tstatus=status: self.show_edit_table_popup(tid, tnum, tstatus),
                width=40,
                height=40,
                fg_color=(self.primary_color, self.primary_dark),
                corner_radius=10
            )
            edit_button.pack(side="left", padx=5)
            edit_button.bind("<Enter>", lambda event, b=edit_button: self.on_action_button_enter(event, b, self.primary_color, self.primary_dark))
            edit_button.bind("<Leave>", lambda event, b=edit_button: self.on_action_button_leave(event, b, self.primary_color, self.primary_dark))
            remove_button = ctk.CTkButton(
                master=button_frame,
                text="" if self.remove_icon else "Remove",
                image=self.remove_icon,
                command=lambda tid=table_id: self.remove_table(tid),
                width=40,
                height=40,
                fg_color=(self.delete_color, self.delete_dark),
                corner_radius=10
            )
            remove_button.pack(side="left", padx=5)
            remove_button.bind("<Enter>", lambda event, b=remove_button: self.on_action_button_enter(event, b, self.delete_color, self.delete_dark))
            remove_button.bind("<Leave>", lambda event, b=remove_button: self.on_action_button_leave(event, b, self.delete_color, self.delete_dark))
        for i in range(num_rows):
            self.tables_frame.grid_rowconfigure(i, weight=1, minsize=190)
        for j in range(num_columns):
            self.tables_frame.grid_columnconfigure(j, weight=1, minsize=340)
        self.tables_frame.grid_propagate(False)

    def show_add_table_popup(self):
        popup = ctk.CTkToplevel(self.root)
        popup.title("Add New Table")
        popup_width = 400
        popup_height = 250
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_position = (screen_width - popup_width) // 2
        y_position = (screen_height - popup_height) // 2
        popup.geometry(f"{popup_width}x{popup_height}+{x_position}+{y_position}")
        popup.transient(self.root)
        popup.grab_set()
        number_label = ctk.CTkLabel(popup, text="Table Number:", font=self.font_subtitle, text_color=self.text_color)
        number_label.pack(pady=(20, 0))
        number_entry = ctk.CTkEntry(
            popup,
            width=200,
            height=40,
            font=self.font_subtitle,
            fg_color="#F9F7F0",
            text_color=self.text_color,
            border_width=1,
            border_color=self.shadow_color,
            corner_radius=10
        )
        number_entry.pack(pady=(0, 20))
        def save():
            table_number_str = number_entry.get().strip()
            if not table_number_str:
                messagebox.showerror("Error", "Table number is required.", parent=popup)
                return
            try:
                table_number = int(table_number_str)
                if table_number <= 0:
                    raise ValueError("Table number must be a positive integer.")
            except ValueError:
                messagebox.showerror("Error", "Table number must be a positive integer.", parent=popup)
                return
            try:
                from db_connection import add_table
                success = add_table(table_number, status="empty")
                if success:
                    messagebox.showinfo("Success", "Table added successfully!", parent=popup)
                    popup.destroy()
                    self.all_tables = []
                    self.show_tables()
                else:
                    messagebox.showerror("Error", "Failed to add table.", parent=popup)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add table: {e}", parent=popup)
        save_button = ctk.CTkButton(
            popup,
            text="Save",
            command=save,
            font=self.font_button,
            width=100,
            height=40,
            fg_color=(self.primary_color, self.primary_dark),
            text_color="white",
            corner_radius=10,
            border_width=2,
            border_color=self.primary_dark
        )
        save_button.pack(pady=10)
        save_button.bind("<Enter>", lambda event, b=save_button: self.on_action_button_enter(event, b, self.primary_color, self.primary_dark))
        save_button.bind("<Leave>", lambda event, b=save_button: self.on_action_button_leave(event, b, self.primary_color, self.primary_dark))
        cancel_button = ctk.CTkButton(
            popup,
            text="Cancel",
            command=popup.destroy,
            font=self.font_button,
            width=100,
            height=40,
            fg_color=(self.primary_color, self.primary_dark),
            text_color="white",
            corner_radius=10,
            border_width=2,
            border_color=self.primary_dark
        )
        cancel_button.pack(pady=10)
        cancel_button.bind("<Enter>", lambda event, b=cancel_button: self.on_action_button_enter(event, b, self.primary_color, self.primary_dark))
        cancel_button.bind("<Leave>", lambda event, b=cancel_button: self.on_action_button_leave(event, b, self.primary_color, self.primary_dark))

    def show_edit_table_popup(self, table_id, table_number, status):
        popup = ctk.CTkToplevel(self.root)
        popup.title(f"Edit Table {table_number}")
        popup_width = 400
        popup_height = 250
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_position = (screen_width - popup_width) // 2
        y_position = (screen_height - popup_height) // 2
        popup.geometry(f"{popup_width}x{popup_height}+{x_position}+{y_position}")
        popup.transient(self.root)
        popup.grab_set()
        number_label = ctk.CTkLabel(popup, text="Table Number:", font=self.font_subtitle, text_color=self.text_color)
        number_label.pack(pady=(20, 0))
        number_entry = ctk.CTkEntry(
            popup,
            width=200,
            height=40,
            font=self.font_subtitle,
            fg_color="#F9F7F0",
            text_color=self.text_color,
            border_width=1,
            border_color=self.shadow_color,
            corner_radius=10
        )
        number_entry.insert(0, str(table_number))
        number_entry.pack(pady=(0, 20))
        status_label = ctk.CTkLabel(popup, text=f"Status: {status}", font=self.font_subtitle, text_color=self.text_color)
        status_label.pack(pady=(10, 0))
        def save():
            table_number_str = number_entry.get().strip()
            if not table_number_str:
                messagebox.showerror("Error", "Table number is required.", parent=popup)
                return
            try:
                table_number = int(table_number_str)
                if table_number <= 0:
                    raise ValueError("Table number must be a positive integer.")
            except ValueError:
                messagebox.showerror("Error", "Table number must be a positive integer.", parent=popup)
                return
            try:
                from db_connection import update_table
                success = update_table(table_id, table_number, status)
                if success:
                    messagebox.showinfo("Success", "Table updated successfully!", parent=popup)
                    popup.destroy()
                    self.all_tables = []
                    self.show_tables()
                else:
                    messagebox.showerror("Error", "Table not found.", parent=popup)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update table: {e}", parent=popup)
        save_button = ctk.CTkButton(
            popup,
            text="Save",
            command=save,
            font=self.font_button,
            width=100,
            height=40,
            fg_color=(self.primary_color, self.primary_dark),
            text_color="white",
            corner_radius=10,
            border_width=2,
            border_color=self.primary_dark
        )
        save_button.pack(pady=10)
        save_button.bind("<Enter>", lambda event, b=save_button: self.on_action_button_enter(event, b, self.primary_color, self.primary_dark))
        save_button.bind("<Leave>", lambda event, b=save_button: self.on_action_button_leave(event, b, self.primary_color, self.primary_dark))
        cancel_button = ctk.CTkButton(
            popup,
            text="Cancel",
            command=popup.destroy,
            font=self.font_button,
            width=100,
            height=40,
            fg_color=(self.primary_color, self.primary_dark),
            text_color="white",
            corner_radius=10,
            border_width=2,
            border_color=self.primary_dark
        )
        cancel_button.pack(pady=10)
        cancel_button.bind("<Enter>", lambda event, b=cancel_button: self.on_action_button_enter(event, b, self.primary_color, self.primary_dark))
        cancel_button.bind("<Leave>", lambda event, b=cancel_button: self.on_action_button_leave(event, b, self.primary_color, self.primary_dark))

    def remove_table(self, table_id):
        if messagebox.askyesno("Confirm", "Are you sure you want to remove this table?"):
            try:
                from db_connection import delete_table
                success = delete_table(table_id)
                if success:
                    self.all_tables = [table for table in self.all_tables if table[0] != table_id]
                    messagebox.showinfo("Info", "Table removed successfully!")
                    self.show_tables()
                else:
                    messagebox.showerror("Error", "Table not found.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

    def back_to_main(self):
        try:
            from main_screen import MainScreen
            for widget in self.root.winfo_children():
                widget.destroy()
            MainScreen(self.root, self.role)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to return to main screen: {e}")