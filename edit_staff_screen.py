import customtkinter as ctk
from tkinter import messagebox
from db_connection import update_staff
from PIL import Image
import os

class EditStaffScreen:
    def __init__(self, root, role, staff_id, username, password):
        self.root = root
        self.role = role
        self.staff_id = staff_id
        self.root.title("Restaurant Management - Edit Staff")
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
        self.delete_color = "#FF6F61"
        self.delete_dark = "#D94F43"
        self.background_start = "#F2EFE7"
        self.background_end = "#E8E4D9"
        self.text_color = "#48A6A7"
        self.header_color = "#006A71"
        self.shadow_color = "#D3CFC3"
        self.font_title = ("Helvetica", 24, "bold")
        self.font_subtitle = ("Helvetica", 16, "bold")
        self.font_button = ("Helvetica", 14, "bold")
        self.font_entry = ("Helvetica", 14)
        self.show_edit_staff_form(username, password)

    def darken_color(self, hex_color):
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = max(0, int(r * 0.8))
        g = max(0, int(g * 0.8))
        b = max(0, int(b * 0.8))
        return f"#{r:02x}{g:02x}{b:02x}"

    def on_button_enter(self, event, button, original_gradient_start, original_gradient_end):
        darkened_start = self.darken_color(original_gradient_start)
        darkened_end = self.darken_color(original_gradient_end)
        button.configure(fg_color=(darkened_start, darkened_end))

    def on_button_leave(self, event, button, original_gradient_start, original_gradient_end):
        button.configure(fg_color=(original_gradient_start, original_gradient_end))

    def show_edit_staff_form(self, username, password):
        main_frame = ctk.CTkFrame(self.root, fg_color=(self.background_start, self.background_end))
        main_frame.pack(fill="both", expand=True)
        logo_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        logo_frame.pack(pady=40)
        try:
            logo_path = os.path.join("icons", "logo.png")
            if not os.path.exists(logo_path):
                raise FileNotFoundError
            logo_image = Image.open(logo_path)
            logo_image = logo_image.resize((60, 60), Image.Resampling.LANCZOS)
            logo_ctk_image = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(60, 60))
            ctk.CTkLabel(logo_frame, image=logo_ctk_image, text="").pack()
        except Exception as e:
            ctk.CTkLabel(
                logo_frame,
                text="🍽️",
                font=("Helvetica", 60),
                text_color=self.header_color
            ).pack()
        ctk.CTkLabel(
            logo_frame,
            text="Edit Staff",
            font=self.font_title,
            text_color=self.header_color
        ).pack(pady=10)
        form_frame = ctk.CTkFrame(
            main_frame,
            fg_color="white",
            corner_radius=20,
            border_width=2,
            border_color=self.shadow_color
        )
        form_frame.pack(pady=30, padx=20)
        edit_username_var = ctk.StringVar(value=username)
        ctk.CTkLabel(
            form_frame,
            text="Username",
            font=self.font_subtitle,
            text_color=self.text_color
        ).pack(pady=(30, 5), padx=30)
        ctk.CTkEntry(
            form_frame,
            textvariable=edit_username_var,
            font=self.font_entry,
            width=300,
            height=40,
            fg_color="#F9F7F0",
            text_color=self.text_color,
            border_width=1,
            border_color=self.shadow_color,
            corner_radius=10
        ).pack(pady=5, padx=30)
        edit_password_var = ctk.StringVar(value=password)
        ctk.CTkLabel(
            form_frame,
            text="Password",
            font=self.font_subtitle,
            text_color=self.text_color
        ).pack(pady=(20, 5), padx=30)
        ctk.CTkEntry(
            form_frame,
            textvariable=edit_password_var,
            font=self.font_entry,
            width=300,
            height=40,
            fg_color="#F9F7F0",
            text_color=self.text_color,
            border_width=1,
            border_color=self.shadow_color,
            corner_radius=10,
            show="*"
        ).pack(pady=(5, 30), padx=30)
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=30)
        save_button = ctk.CTkButton(
            button_frame,
            text="Save",
            command=lambda: self.update_staff(edit_username_var.get(), edit_password_var.get()),
            font=self.font_button,
            width=200,
            height=50,
            fg_color=(self.accent_color, self.accent_dark),
            text_color="black",
            corner_radius=10,
            border_width=2,
            border_color=self.accent_dark
        )
        save_button.pack(side="left", padx=10)
        save_button.bind("<Enter>", lambda event, b=save_button: self.on_button_enter(event, b, self.accent_color, self.accent_dark))
        save_button.bind("<Leave>", lambda event, b=save_button: self.on_button_leave(event, b, self.accent_color, self.accent_dark))
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.back_to_manage_staffs,
            font=self.font_button,
            width=200,
            height=50,
            fg_color=(self.delete_color, self.delete_dark),
            text_color="white",
            corner_radius=10,
            border_width=2,
            border_color=self.delete_dark
        )
        cancel_button.pack(side="left", padx=10)
        cancel_button.bind("<Enter>", lambda event, b=cancel_button: self.on_button_enter(event, b, self.delete_color, self.delete_dark))
        cancel_button.bind("<Leave>", lambda event, b=cancel_button: self.on_button_leave(event, b, self.delete_color, self.delete_dark))

    def update_staff(self, username, password):
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        try:
            if update_staff(self.staff_id, username, password):
                messagebox.showinfo("Success", f"Staff account updated successfully!")
                self.back_to_manage_staffs()
            else:
                messagebox.showerror("Error", "Username already exists or staff not found")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def back_to_manage_staffs(self):
        from manage_staffs import ManageStaffs
        for widget in self.root.winfo_children():
            widget.destroy()
        ManageStaffs(self.root, self.role)