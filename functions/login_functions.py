from tkinter import messagebox
from db_connection import verify_login
from main_screen import MainScreen
import os
import json

def login(username_var, password_var, root, save_credentials):
    username = username_var.get().strip()
    password = password_var.get().strip()
    if not username or not password:
        messagebox.showerror("Error", "Please enter both username and password")
        return
    try:
        role = verify_login(username, password)
        if role:
            save_credentials()
            for widget in root.winfo_children():
                widget.destroy()
            MainScreen(root, role)
        else:
            messagebox.showerror("Error", "Invalid username or password")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def save_credentials(username_var, password_var, remember_me_var):
    data = {
        "username": username_var.get().strip(),
        "password": password_var.get().strip(),
        "remember_me": remember_me_var.get()
    }
    try:
        if remember_me_var.get():
            with open("login_credentials.json", "w") as f:
                json.dump(data, f)
        else:
            if os.path.exists("login_credentials.json"):
                os.remove("login_credentials.json")
    except Exception as e:
        print(f"Error saving credentials: {e}")

def load_credentials(username_var, password_var, remember_me_var):
    try:
        if os.path.exists("login_credentials.json"):
            with open("login_credentials.json", "r") as f:
                data = json.load(f)
                if data.get("remember_me", False):
                    username_var.set(data.get("username", ""))
                    password_var.set(data.get("password", ""))
                    remember_me_var.set(True)
    except Exception as e:
        print(f"Error loading credentials: {e}")