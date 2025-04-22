import customtkinter as ctk
from login_screen import LoginScreen

if __name__ == "__main__":
    try:
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("green")
        root = ctk.CTk()
        app = LoginScreen(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")