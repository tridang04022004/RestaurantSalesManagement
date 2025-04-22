import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import shutil
from datetime import datetime
from db_connection import update_category, get_all_categories
from PIL import Image

class EditCategoryScreen:
    def __init__(self, root, role, category_id, category_name):
        self.root = root
        self.role = role
        self.category_id = category_id
        self.current_img_path = None
        self.root.title("Restaurant Management - Edit Category")
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
        self.success_color = "#006A71"
        self.error_color = "#FF6F61"
        self.font_title = ("Helvetica", 24, "bold")
        self.font_subtitle = ("Helvetica", 16, "bold")
        self.font_button = ("Helvetica", 14, "bold")
        self.font_entry = ("Helvetica", 14)
        self.message_label = None
        self.new_image_path = None
        self.image_preview_label = None
        categories = get_all_categories()
        for cat_id, _, img_path in categories:
            if cat_id == self.category_id:
                self.current_img_path = img_path
                break
        self.show_edit_category_form(category_name)

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

    def show_edit_category_form(self, category_name):
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
            text="Edit Category",
            font=self.font_title,
            text_color=self.header_color
        ).pack(pady=10)
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        form_wrapper = ctk.CTkFrame(content_frame, fg_color="transparent")
        form_wrapper.pack(expand=True)
        form_frame = ctk.CTkFrame(
            form_wrapper,
            fg_color="white",
            corner_radius=20,
            border_width=2,
            border_color=self.shadow_color
        )
        form_frame.pack(pady=30, padx=20)
        self.edit_category_var = ctk.StringVar(value=category_name)
        ctk.CTkLabel(
            form_frame,
            text="Category Name:",
            font=self.font_subtitle,
            text_color=self.text_color
        ).pack(pady=(30, 5), padx=30)
        self.category_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.edit_category_var,
            font=self.font_entry,
            width=300,
            height=40,
            fg_color="#F9F7F0",
            text_color=self.text_color,
            border_width=1,
            border_color=self.shadow_color,
            corner_radius=10
        )
        self.category_entry.pack(pady=5, padx=30)
        ctk.CTkLabel(
            form_frame,
            text="Category Image:",
            font=self.font_subtitle,
            text_color=self.text_color
        ).pack(pady=(20, 5), padx=30)
        self.select_image_button = ctk.CTkButton(
            form_frame,
            text="Change Image",
            command=self.select_image,
            font=self.font_button,
            width=200,
            height=40,
            fg_color=(self.primary_color, self.primary_dark),
            text_color="white",
            corner_radius=10,
            border_width=2,
            border_color=self.primary_dark
        )
        self.select_image_button.pack(pady=5, padx=30)
        self.select_image_button.bind("<Enter>", lambda event, b=self.select_image_button: self.on_button_enter(event, b, self.primary_color, self.primary_dark))
        self.select_image_button.bind("<Leave>", lambda event, b=self.select_image_button: self.on_button_leave(event, b, self.primary_color, self.primary_dark))
        self.image_preview_label = ctk.CTkLabel(
            form_frame,
            text="Image preview",
            width=400,
            height=100,
            fg_color="#F9F7F0",
            text_color=self.text_color,
            corner_radius=10,
            font=self.font_subtitle
        )
        self.image_preview_label.pack(pady=(20, 30), padx=30)
        if self.current_img_path and os.path.exists(self.current_img_path):
            self.load_current_image()
        self.message_label = ctk.CTkLabel(content_frame, text="", font=self.font_entry, text_color=self.text_color)
        self.message_label.pack(pady=10)
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.pack(pady=30)
        save_button = ctk.CTkButton(
            button_frame,
            text="Save",
            command=lambda: self.update_category(self.edit_category_var.get()),
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
            command=self.back_to_menu,
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

    def load_current_image(self):
        try:
            image = Image.open(self.current_img_path)
            image = image.resize((400, 100), Image.Resampling.LANCZOS)
            ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=(400, 100))
            self.image_preview_label.configure(image=ctk_image, text="")
        except Exception as e:
            self.show_message(f"Failed to load current image: {e}", self.error_color)

    def select_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if file_path:
            self.new_image_path = file_path
            self.show_message("New image selected successfully!", self.success_color)
            try:
                image = Image.open(file_path)
                image = image.resize((400, 100), Image.Resampling.LANCZOS)
                ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=(400, 100))
                self.image_preview_label.configure(image=ctk_image, text="")
            except Exception as e:
                self.show_message(f"Failed to load new image: {e}", self.error_color)

    def update_category(self, name):
        if not name.strip():
            self.show_message("Please enter a category name", self.error_color)
            return
        img_path_to_save = self.current_img_path
        if self.new_image_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = os.path.splitext(self.new_image_path)[1]
            new_filename = f"{timestamp}{file_extension}"
            destination_path = os.path.join("catimg", new_filename)
            try:
                os.makedirs("catimg", exist_ok=True)
                shutil.copy(self.new_image_path, destination_path)
                img_path_to_save = destination_path
                if self.current_img_path and os.path.exists(self.current_img_path):
                    os.remove(self.current_img_path)
            except Exception as e:
                self.show_message(f"Error handling image: {e}", self.error_color)
                if os.path.exists(destination_path):
                    os.remove(destination_path)
                return
        try:
            if update_category(self.category_id, name, img_path_to_save):
                self.show_message(f"Category updated successfully!", self.success_color)
                self.root.after(2000, self.back_to_menu)
            else:
                self.show_message("Category name already exists or category not found", self.error_color)
                if self.new_image_path and os.path.exists(img_path_to_save):
                    os.remove(img_path_to_save)
        except Exception as e:
            self.show_message(f"An error occurred: {e}", self.error_color)
            if self.new_image_path and os.path.exists(img_path_to_save):
                os.remove(img_path_to_save)

    def show_message(self, message, color):
        self.message_label.configure(text=message, text_color=color)
        self.root.after(3000, lambda: self.message_label.configure(text=""))

    def back_to_menu(self):
        from menu_screen import MenuScreen
        for widget in self.root.winfo_children():
            widget.destroy()
        MenuScreen(self.root, self.role)