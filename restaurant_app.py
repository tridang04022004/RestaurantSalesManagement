# restaurant_app.py
import tkinter as tk
from tkinter import messagebox
from db_connection import verify_login  # Import from the new file

class RestaurantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Restaurant Management - Login")
        self.root.geometry("600x700")
        self.root.configure(bg="#FFFFFF")

        # Variables for login
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        # Styling
        self.blue_accent = "#1E90FF"
        self.dark_blue = "#4169E1"
        self.font_large = ("Helvetica", 18, "bold")
        self.font_medium = ("Helvetica", 14)

        # Create login UI
        self.create_login_screen()

    def create_login_screen(self):
        # Header
        header = tk.Label(self.root, text="Restaurant Management", font=self.font_large, bg="#FFFFFF", fg=self.dark_blue)
        header.pack(pady=60)

        # Login Frame
        login_frame = tk.Frame(self.root, bg="#FFFFFF")
        login_frame.pack(pady=30)

        # Username Label and Rounded Entry
        tk.Label(login_frame, text="Username", font=self.font_medium, bg="#FFFFFF", fg=self.dark_blue).grid(row=0, column=0, pady=15, padx=15, sticky="w")
        username_canvas = tk.Canvas(login_frame, width=300, height=40, bg="#FFFFFF", highlightthickness=0)
        username_canvas.grid(row=0, column=1, pady=15)
        self.create_rounded_entry(username_canvas, 300, 40, "#F0F8FF", self.username_var)

        # Password Label and Rounded Entry
        tk.Label(login_frame, text="Password", font=self.font_medium, bg="#FFFFFF", fg=self.dark_blue).grid(row=1, column=0, pady=15, padx=15, sticky="w")
        password_canvas = tk.Canvas(login_frame, width=300, height=40, bg="#FFFFFF", highlightthickness=0)
        password_canvas.grid(row=1, column=1, pady=15)
        self.create_rounded_entry(password_canvas, 300, 40, "#F0F8FF", self.password_var, show="*")

        # Login Button with rounded corners
        button_frame = tk.Frame(self.root, bg="#FFFFFF")
        button_frame.pack(pady=40)
        login_btn = tk.Canvas(button_frame, width=200, height=50, bg="#FFFFFF", highlightthickness=0)
        login_btn.pack()
        self.create_rounded_button(login_btn, 200, 50, self.blue_accent, "Login", self.login)

    def create_rounded_entry(self, canvas, width, height, bg_color, textvariable, show=None):
        # Draw rounded rectangle for the entry background
        canvas.create_oval(5, 5, 45, height-5, fill=bg_color, outline=bg_color)
        canvas.create_oval(width-45, 5, width-5, height-5, fill=bg_color, outline=bg_color)
        canvas.create_rectangle(25, 5, width-25, height-5, fill=bg_color, outline=bg_color)
        # Place Entry widget on top
        entry = tk.Entry(canvas, textvariable=textvariable, font=self.font_medium, bg=bg_color, fg="#000000", borderwidth=0, highlightthickness=0)
        if show:
            entry.config(show=show)
        canvas.create_window(width//2, height//2, window=entry, width=width-50)

    def create_rounded_button(self, canvas, width, height, bg_color, text, command):
        # Draw rounded rectangle
        canvas.create_oval(5, 5, 45, 45, fill=bg_color, outline=bg_color)
        canvas.create_oval(width-45, 5, width-5, 45, fill=bg_color, outline=bg_color)
        canvas.create_rectangle(25, 5, width-25, height-5, fill=bg_color, outline=bg_color)
        # Add text
        canvas.create_text(width//2, height//2, text=text, font=self.font_medium, fill="#FFFFFF")
        # Bind click event
        canvas.bind("<Button-1>", lambda e: command())

    def login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return

        # Use the verify_login function from db_connection
        try:
            role = verify_login(username, password)
            if role:
                # Clear login screen and show main app
                for widget in self.root.winfo_children():
                    widget.destroy()
                self.show_main_app(role)
            else:
                messagebox.showerror("Error", "Invalid username or password")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def show_main_app(self, role):
        # Main app interface in the same window
        self.root.title(f"Restaurant Management - {role.capitalize()}")
        self.root.geometry("800x600")

        tk.Label(self.root, text=f"Welcome, {role}!", font=self.font_large, bg="#FFFFFF", fg=self.dark_blue).pack(pady=30)

        # Buttons with rounded corners
        button_frame = tk.Frame(self.root, bg="#FFFFFF")
        button_frame.pack(pady=20)

        if role == "admin":
            add_staff_btn = tk.Canvas(button_frame, width=200, height=50, bg="#FFFFFF", highlightthickness=0)
            add_staff_btn.pack(pady=10)
            self.create_rounded_button(add_staff_btn, 200, 50, self.blue_accent, "Add Staff Account", self.placeholder_function)

        dishes_btn = tk.Canvas(button_frame, width=200, height=50, bg="#FFFFFF", highlightthickness=0)
        dishes_btn.pack(pady=10)
        self.create_rounded_button(dishes_btn, 200, 50, self.blue_accent, "Manage Dishes", self.placeholder_function)

        tables_btn = tk.Canvas(button_frame, width=200, height=50, bg="#FFFFFF", highlightthickness=0)
        tables_btn.pack(pady=10)
        self.create_rounded_button(tables_btn, 200, 50, self.blue_accent, "Manage Tables", self.placeholder_function)

        invoices_btn = tk.Canvas(button_frame, width=200, height=50, bg="#FFFFFF", highlightthickness=0)
        invoices_btn.pack(pady=10)
        self.create_rounded_button(invoices_btn, 200, 50, self.blue_accent, "Manage Invoices", self.placeholder_function)

    def placeholder_function(self):
        # Temporary placeholder for button actions
        messagebox.showinfo("Info", "This feature is not yet implemented.")

if __name__ == "__main__":
    root = tk.Tk()
    app = RestaurantApp(root)
    root.mainloop()