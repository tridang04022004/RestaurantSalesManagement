import customtkinter as ctk
from tkinter import messagebox
from db_connection import verify_login
from main_screen import MainScreen
from PIL import Image
import os
import json

class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Restaurant Management - Login")
        window_width = 600
        window_height = 700
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.username_var = ctk.StringVar()
        self.password_var = ctk.StringVar()
        self.remember_me_var = ctk.BooleanVar(value=False)
        self.primary_color = "#9ACBD0"
        self.primary_dark = "#006A71"
        self.accent_color = "#FFCA28"
        self.accent_dark = "#FFB300"
        self.background_start = "#F2EFE7"
        self.background_end = "#E8E4D9"
        self.text_color = "#48A6A7"
        self.header_color = "#006A71"
        self.shadow_color = "#D3CFC3"
        self.entry_bg = "#F9F7F0"
        self.font_title = ("Helvetica", 24, "bold")
        self.font_subtitle = ("Helvetica", 16, "bold")
        self.font_button = ("Helvetica", 14, "bold")
        self.font_entry = ("Helvetica", 14)
        self.font_checkbox = ("Helvetica", 12)
        self.load_credentials()
        self.create_login_screen()

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

    def load_credentials(self):
        try:
            if os.path.exists("login_credentials.json"):
                with open("login_credentials.json", "r") as f:
                    data = json.load(f)
                    if data.get("remember_me", False):
                        self.username_var.set(data.get("username", ""))
                        self.password_var.set(data.get("password", ""))
                        self.remember_me_var.set(True)
        except Exception as e:
            print(f"Error loading credentials: {e}")

    def save_credentials(self):
        data = {
            "username": self.username_var.get().strip(),
            "password": self.password_var.get().strip(),
            "remember_me": self.remember_me_var.get()
        }
        try:
            if self.remember_me_var.get():
                with open("login_credentials.json", "w") as f:
                    json.dump(data, f)
            else:
                if os.path.exists("login_credentials.json"):
                    os.remove("login_credentials.json")
        except Exception as e:
            print(f"Error saving credentials: {e}")

    def create_login_screen(self):
        main_frame = ctk.CTkFrame(self.root, fg_color=(self.background_start, self.background_end))
        main_frame.pack(fill="both", expand=True)
        logo_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        logo_frame.pack(pady=40, expand=True)
        try:
            logo_path = os.path.join("icons", "logo.png")
            if not os.path.exists(logo_path):
                raise FileNotFoundError(f"Logo image not found at {logo_path}")
            logo_image = Image.open(logo_path)
            logo_image = logo_image.resize((60, 60), Image.Resampling.LANCZOS)
            logo_ctk_image = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(60, 60))
            ctk.CTkLabel(logo_frame, image=logo_ctk_image, text="").pack()
        except Exception as e:
            print(f"Error loading logo image: {e}")
            ctk.CTkLabel(
                logo_frame,
                text="🍽️",
                font=("Helvetica", 60),
                text_color=self.header_color
            ).pack()
        ctk.CTkLabel(
            logo_frame,
            text="Restaurant Management",
            font=self.font_title,
            text_color=self.header_color
        ).pack(pady=10)
        login_frame = ctk.CTkFrame(
            main_frame,
            fg_color="white",
            corner_radius=20,
            border_width=2,
            border_color=self.shadow_color
        )
        login_frame.pack(pady=30, padx=50, fill="x")
        ctk.CTkLabel(
            login_frame,
            text="Username",
            font=self.font_subtitle,
            text_color=self.text_color
        ).pack(pady=(20, 5))
        ctk.CTkEntry(
            login_frame,
            textvariable=self.username_var,
            font=self.font_entry,
            width=300,
            height=40,
            fg_color=self.entry_bg,
            text_color=self.text_color,
            border_width=1,
            border_color=self.shadow_color,
            corner_radius=10
        ).pack(pady=5)
        ctk.CTkLabel(
            login_frame,
            text="Password",
            font=self.font_subtitle,
            text_color=self.text_color
        ).pack(pady=(20, 5))
        ctk.CTkEntry(
            login_frame,
            textvariable=self.password_var,
            font=self.font_entry,
            width=300,
            height=40,
            fg_color=self.entry_bg,
            text_color=self.text_color,
            border_width=1,
            border_color=self.shadow_color,
            corner_radius=10,
            show="*"
        ).pack(pady=5)
        ctk.CTkCheckBox(
            login_frame,
            text="Remember Me",
            variable=self.remember_me_var,
            font=self.font_checkbox,
            text_color=self.text_color,
            fg_color=self.primary_color,
            hover_color=self.primary_dark,
            border_color=self.shadow_color,
            corner_radius=5
        ).pack(pady=10)
        login_button = ctk.CTkButton(
            login_frame,
            text="Login",
            command=self.login,
            font=self.font_button,
            width=200,
            height=50,
            fg_color=(self.primary_color, self.primary_dark),
            text_color="white",
            corner_radius=10,
            border_width=2,
            border_color=self.primary_dark
        )
        login_button.pack(pady=40)
        login_button.bind(
            "<Enter>",
            lambda event, b=login_button: self.on_button_enter(event, b, self.primary_color, self.primary_dark)
        )
        login_button.bind(
            "<Leave>",
            lambda event, b=login_button: self.on_button_leave(event, b, self.primary_color, self.primary_dark)
        )

    def login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        try:
            role = verify_login(username, password)
            if role:
                self.save_credentials()
                for widget in self.root.winfo_children():
                    widget.destroy()
                MainScreen(self.root, role)
            else:
                messagebox.showerror("Error", "Invalid username or password")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")