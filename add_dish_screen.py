import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image
import os
import sqlite3
import time

class AddDishScreen:
    def __init__(self, root, role, category_id, category_name):
        self.root = root
        self.role = role
        self.category_id = category_id
        self.category_name = category_name
        self.root.title(f"Restaurant Management - Add Dish to {category_name}")
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
        self.font_title = ("Helvetica", 24, "bold")
        self.font_subtitle = ("Helvetica", 16, "bold")
        self.font_button = ("Helvetica", 14, "bold")
        self.selected_image_path = None
        self.image_preview_label = None
        try:
            self.show_add_dish()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Add Dish screen: {e}")

    def darken_color(self, hex_color):
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = max(0, int(r * 0.8))
        g = max(0, int(g * 0.8))
        b = max(0, int(b * 0.8))
        return f"#{r:02x}{g:02x}{b:02x}"

    def on_action_button_enter(self, event, button, original_gradient_start, original_gradient_end):
        darkened_start = self.darken_color(original_gradient_start)
        darkened_end = self.darken_color(original_gradient_end)
        button.configure(fg_color=(darkened_start, darkened_end))

    def on_action_button_leave(self, event, button, original_gradient_start, original_gradient_end):
        button.configure(fg_color=(original_gradient_start, original_gradient_end))

    def show_add_dish(self):
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
            command=self.back_to_dishes
        )
        back_button.pack(side="left")
        back_button.bind("<Enter>", lambda event, b=back_button: self.on_action_button_enter(event, b, self.primary_color, self.primary_dark))
        back_button.bind("<Leave>", lambda event, b=back_button: self.on_action_button_leave(event, b, self.primary_color, self.primary_dark))
        ctk.CTkLabel(
            top_bar,
            text=f"Add Dish to {self.category_name}",
            font=self.font_title,
            text_color=self.header_color
        ).pack(side="left", padx=20)
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
        left_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        left_frame.pack(side="left", padx=20, pady=20)
        dish_name_label = ctk.CTkLabel(left_frame, text="Dish name:", font=self.font_subtitle, text_color=self.text_color)
        dish_name_label.pack(pady=(0, 5))
        self.dish_name_entry = ctk.CTkEntry(
            left_frame,
            width=300,
            height=40,
            font=self.font_subtitle,
            fg_color="#F9F7F0",
            text_color=self.text_color,
            border_width=1,
            border_color=self.shadow_color,
            corner_radius=10
        )
        self.dish_name_entry.pack(pady=5)
        price_label = ctk.CTkLabel(left_frame, text="Price:", font=self.font_subtitle, text_color=self.text_color)
        price_label.pack(pady=(20, 5))
        self.price_entry = ctk.CTkEntry(
            left_frame,
            width=300,
            height=40,
            font=self.font_subtitle,
            fg_color="#F9F7F0",
            text_color=self.text_color,
            border_width=1,
            border_color=self.shadow_color,
            corner_radius=10
        )
        self.price_entry.pack(pady=5)
        category_label = ctk.CTkLabel(left_frame, text="Category:", font=self.font_subtitle, text_color=self.text_color)
        category_label.pack(pady=(20, 5))
        try:
            from db_connection import get_all_categories
            categories = get_all_categories()
            category_names = [cat[1] for cat in categories]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch categories: {e}")
            return
        self.category_var = ctk.StringVar(value=self.category_name)
        self.category_dropdown = ctk.CTkComboBox(
            left_frame,
            values=category_names,
            variable=self.category_var,
            width=300,
            height=40,
            font=self.font_subtitle,
            fg_color="#F9F7F0",
            text_color=self.text_color,
            dropdown_fg_color="#F9F7F0",
            dropdown_text_color=self.text_color,
            border_width=1,
            border_color=self.shadow_color,
            corner_radius=10
        )
        self.category_dropdown.pack(pady=5)
        right_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        right_frame.pack(side="right", padx=20, pady=20)
        upload_button = ctk.CTkButton(
            right_frame,
            text="Upload Image",
            command=self.upload_image,
            font=self.font_button,
            width=200,
            height=40,
            fg_color=(self.primary_color, self.primary_dark),
            text_color="white",
            corner_radius=10,
            border_width=2,
            border_color=self.primary_dark
        )
        upload_button.pack(pady=(0, 5))
        upload_button.bind("<Enter>", lambda event, b=upload_button: self.on_action_button_enter(event, b, self.primary_color, self.primary_dark))
        upload_button.bind("<Leave>", lambda event, b=upload_button: self.on_action_button_leave(event, b, self.primary_color, self.primary_dark))
        self.image_preview_label = ctk.CTkLabel(
            right_frame,
            text="Image preview",
            width=200,
            height=200,
            fg_color="#F9F7F0",
            text_color=self.text_color,
            corner_radius=10,
            font=self.font_subtitle
        )
        self.image_preview_label.pack(pady=5)
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.pack(side="bottom", pady=20)
        save_button = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save_dish,
            font=self.font_button,
            width=200,
            height=50,
            fg_color=(self.primary_color, self.primary_dark),
            text_color="white",
            corner_radius=10,
            border_width=2,
            border_color=self.primary_dark
        )
        save_button.pack()
        save_button.bind("<Enter>", lambda event, b=save_button: self.on_action_button_enter(event, b, self.primary_color, self.primary_dark))
        save_button.bind("<Leave>", lambda event, b=save_button: self.on_action_button_leave(event, b, self.primary_color, self.primary_dark))

    def upload_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            self.selected_image_path = file_path
            try:
                image = Image.open(file_path)
                image = image.resize((200, 200), Image.Resampling.LANCZOS)
                ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=(200, 200))
                self.image_preview_label.configure(image=ctk_image, text="")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")

    def save_dish(self):
        dish_name = self.dish_name_entry.get().strip()
        price_str = self.price_entry.get().strip()
        category_name = self.category_var.get()
        if not dish_name:
            messagebox.showerror("Error", "Dish name is required.")
            return
        try:
            price = float(price_str)
            if price <= 0:
                raise ValueError("Price must be greater than 0.")
        except ValueError:
            messagebox.showerror("Error", "Price must be a valid positive number.")
            return
        try:
            conn = sqlite3.connect('restaurant.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Error", "Selected category not found.")
                conn.close()
                return
            category_id = result[0]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch category: {e}")
            conn.close()
            return
        finally:
            conn.close()
        img_path = None
        if self.selected_image_path:
            try:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                img_extension = os.path.splitext(self.selected_image_path)[1]
                img_filename = f"img/{timestamp}{img_extension}"
                os.makedirs("img", exist_ok=True)
                image = Image.open(self.selected_image_path)
                image.save(img_filename)
                img_path = img_filename
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {e}")
                return
        try:
            conn = sqlite3.connect('restaurant.db')
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO dishes (name, price, category_id, img_path) VALUES (?, ?, ?, ?)",
                (dish_name, price, category_id, img_path)
            )
            conn.commit()
            messagebox.showinfo("Success", "Dish added successfully!")
            self.back_to_dishes()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save dish: {e}")
        finally:
            conn.close()

    def back_to_dishes(self):
        try:
            from dishes_screen import DishesScreen
            for widget in self.root.winfo_children():
                widget.destroy()
            DishesScreen(self.root, self.role, self.category_id, self.category_name)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to return to dishes screen: {e}")