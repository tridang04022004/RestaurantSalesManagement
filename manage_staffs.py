import customtkinter as ctk
from tkinter import messagebox, ttk
from db_connection import delete_staff, get_all_staff
from add_staff_screen import AddStaffScreen
from edit_staff_screen import EditStaffScreen

class ManageStaffs:
    def __init__(self, root, role):
        self.root = root
        self.role = role
        self.root.title("Restaurant Management - Manage Staffs")
        self.root.geometry("1600x900")
        self.primary_color = "#9ACBD0"
        self.primary_dark = "#006A71"
        self.accent_color = "#9ACBD0"
        self.accent_dark = "#006A71"
        self.background_start = "#F2EFE7"
        self.background_end = "#E8E4D9"
        self.text_color = "#48A6A7"
        self.header_color = "#006A71"
        self.header_text_color = "#006A71"
        self.row_color_1 = "#F9F7F0"
        self.row_color_2 = "#EFEBE0"
        self.hover_color = "#D1E8E8"
        self.selected_color = "#48A6A7"
        self.table_bg_start = "#F9F7F0"
        self.table_bg_end = "#EFEBE0"
        self.font_title = ("Helvetica", 24, "bold")
        self.font_header = ("Helvetica", 16, "bold")
        self.font_body = ("Helvetica", 14)
        self.font_button = ("Helvetica", 14, "bold")
        self.show_manage_staffs()

    def darken_color(self, hex_color):
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = max(0, int(r * 0.8))
        g = max(0, int(g * 0.8))
        b = max(0, int(b * 0.8))
        return f"#{r:02x}{g:02x}{b:02x}"

    def on_row_enter(self, event):
        item = self.staff_tree.identify_row(event.y)
        if item:
            self.staff_tree.tag_configure(item, background=self.hover_color)

    def on_row_leave(self, event):
        item = self.staff_tree.identify_row(event.y)
        if item:
            index = self.staff_tree.index(item)
            original_color = self.row_color_1 if index % 2 == 0 else self.row_color_2
            self.staff_tree.tag_configure(item, background=original_color)

    def on_action_button_enter(self, event, button, original_gradient_start, original_gradient_end):
        darkened_start = self.darken_color(original_gradient_start)
        darkened_end = self.darken_color(original_gradient_end)
        button.configure(fg_color=(darkened_start, darkened_end))

    def on_action_button_leave(self, event, button, original_gradient_start, original_gradient_end):
        button.configure(fg_color=(original_gradient_start, original_gradient_end))

    def show_manage_staffs(self):
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
            text="Manage Staffs",
            font=self.font_title,
            text_color=self.header_color
        ).pack(side="left", padx=20)
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        table_container = ctk.CTkFrame(
            content_frame,
            fg_color=(self.table_bg_start, self.table_bg_end),
            corner_radius=15,
            border_width=2,
            border_color=(self.primary_color, self.primary_dark)
        )
        table_container.pack(side="left", fill="both", expand=True, padx=50, pady=20)
        table_frame = ctk.CTkFrame(table_container, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.staff_tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Username", "Password"),
            show="headings",
            height=25
        )
        self.staff_tree.heading("ID", text="ID")
        self.staff_tree.heading("Username", text="Username")
        self.staff_tree.heading("Password", text="Password")
        self.staff_tree.column("ID", width=300, anchor="center")
        self.staff_tree.column("Username", width=450, anchor="center")
        self.staff_tree.column("Password", width=450, anchor="center")
        style = ttk.Style()
        style.configure(
            "Treeview.Heading",
            background=self.primary_color,
            foreground=self.header_text_color,
            font=self.font_header,
            relief="flat",
            padding=10
        )
        style.configure(
            "Treeview",
            rowheight=50,
            font=self.font_body,
            background="transparent",
            foreground=self.text_color,
            fieldbackground="transparent"
        )
        style.map(
            "Treeview",
            background=[('selected', self.selected_color)],
            foreground=[('selected', 'white')]
        )
        self.staff_tree.tag_configure('evenrow', background=self.row_color_1)
        self.staff_tree.tag_configure('oddrow', background=self.row_color_2)
        self.staff_tree.pack(fill="both", expand=True)
        self.staff_tree.bind("<Enter>", self.on_row_enter)
        self.staff_tree.bind("<Leave>", self.on_row_leave)
        self.staff_tree.bind("<Motion>", self.on_row_enter)
        self.load_staff()
        button_frame = ctk.CTkFrame(content_frame, width=300, fg_color="transparent")
        button_frame.pack(side="right", fill="y", padx=20)
        ctk.CTkButton(
            button_frame,
            text="Add New Staff",
            command=self.show_add_staff_form,
            font=self.font_button,
            width=200,
            height=50,
            fg_color=(self.accent_color, self.accent_dark),
            text_color="black",
            corner_radius=10,
            border_width=1,
            border_color=self.accent_dark
        ).pack(pady=20)
        ctk.CTkButton(
            button_frame,
            text="Edit Staff",
            command=self.show_edit_staff_form,
            font=self.font_button,
            width=200,
            height=50,
            fg_color=(self.accent_color, self.accent_dark),
            text_color="black",
            corner_radius=10,
            border_width=1,
            border_color=self.accent_dark
        ).pack(pady=20)
        ctk.CTkButton(
            button_frame,
            text="Remove Staff",
            command=self.remove_staff,
            font=self.font_button,
            width=200,
            height=50,
            fg_color=(self.accent_color, self.accent_dark),
            text_color="black",
            corner_radius=10,
            border_width=1,
            border_color=self.accent_dark
        ).pack(pady=20)
        for button in button_frame.winfo_children():
            button.bind("<Enter>", lambda event, b=button: self.on_action_button_enter(event, b, self.accent_color, self.accent_dark))
            button.bind("<Leave>", lambda event, b=button: self.on_action_button_leave(event, b, self.accent_color, self.accent_dark))

    def load_staff(self):
        try:
            staff_list = get_all_staff()
            for item in self.staff_tree.get_children():
                self.staff_tree.delete(item)
            for idx, staff in enumerate(staff_list):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                self.staff_tree.insert("", "end", values=(staff[0], staff[1], staff[2]), tags=(tag,))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load staff: {e}")

    def show_add_staff_form(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        AddStaffScreen(self.root, self.role)

    def show_edit_staff_form(self):
        selected = self.staff_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a staff account to edit")
            return
        staff_id = self.staff_tree.item(selected[0])["values"][0]
        username = self.staff_tree.item(selected[0])["values"][1]
        password = self.staff_tree.item(selected[0])["values"][2]
        for widget in self.root.winfo_children():
            widget.destroy()
        EditStaffScreen(self.root, self.role, staff_id, username, password)

    def remove_staff(self):
        selected = self.staff_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a staff account to remove")
            return
        staff_id = self.staff_tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Confirm", "Are you sure you want to remove this staff account?"):
            try:
                if delete_staff(staff_id):
                    messagebox.showinfo("Success", "Staff account removed successfully!")
                    self.load_staff()
                else:
                    messagebox.showerror("Error", "Staff account not found")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

    def back_to_main(self):
        from main_screen import MainScreen
        for widget in self.root.winfo_children():
            widget.destroy()
        MainScreen(self.root, self.role)