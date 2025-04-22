import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageEnhance, ImageDraw
import os

class DishesScreen:
    def __init__(self, root, role, category_id, category_name):
        self.root = root
        self.role = role
        self.category_id = category_id
        self.category_name = category_name
        self.root.title(f"Restaurant Management - Dishes in {category_name}")
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
        self.font_dish = ("Helvetica", 20, "bold")
        self.font_price = ("Helvetica", 18)
        self.edit_icon = None
        self.remove_icon = None
        self.search_icon = None
        try:
            edit_icon_path = os.path.join("icons", "edit.png")
            remove_icon_path = os.path.join("icons", "remove.png")
            search_icon_path = os.path.join("icons", "search.png")
            if not os.path.exists(edit_icon_path):
                raise FileNotFoundError
            if not os.path.exists(remove_icon_path):
                raise FileNotFoundError
            if not os.path.exists(search_icon_path):
                raise FileNotFoundError
            edit_icon = Image.open(edit_icon_path)
            remove_icon = Image.open(remove_icon_path)
            search_icon = Image.open(search_icon_path)
            edit_icon = edit_icon.resize((30, 30), Image.Resampling.LANCZOS)
            remove_icon = remove_icon.resize((30, 30), Image.Resampling.LANCZOS)
            search_icon = search_icon.resize((30, 30), Image.Resampling.LANCZOS)
            self.edit_icon = ctk.CTkImage(light_image=edit_icon, dark_image=edit_icon, size=(30, 30))
            self.remove_icon = ctk.CTkImage(light_image=remove_icon, dark_image=remove_icon, size=(30, 30))
            self.search_icon = ctk.CTkImage(light_image=search_icon, dark_image=search_icon, size=(30, 30))
        except Exception as e:
            self.edit_icon = None
            self.remove_icon = None
            self.search_icon = None
        self.all_dishes = []
        self.filtered_dishes = []
        self.selected_dish = None
        self.dish_info_frame = None
        self.dish_info_image_label = None
        try:
            self.show_dishes()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dishes screen: {e}")

    def apply_rounded_corners(self, image, radius):
        try:
            mask = Image.new('L', image.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle([(0, 0), image.size], radius=radius, fill=255)
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            rounded_image = Image.new('RGBA', image.size, (0, 0, 0, 0))
            rounded_image.paste(image, (0, 0), mask)
            return rounded_image
        except Exception as e:
            return image

    def apply_gradient_overlay(self, image):
        gradient = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(gradient)
        for y in range(image.height):
            alpha = int(100 * (y / image.height))
            draw.line([(0, y), (image.width, y)], fill=(0, 0, 0, alpha))
        image.paste(gradient, (0, 0), gradient)
        return image

    def darken_color(self, hex_color):
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = max(0, int(r * 0.8))
        g = max(0, int(g * 0.8))
        b = max(0, int(b * 0.8))
        return f"#{r:02x}{g:02x}{b:02x}"

    def on_dish_frame_enter(self, event, frame):
        frame.configure(fg_color="#D1E8E8")

    def on_dish_frame_leave(self, event, frame):
        frame.configure(fg_color="#F9F7F0")

    def on_action_button_enter(self, event, button, original_gradient_start, original_gradient_end):
        darkened_start = self.darken_color(original_gradient_start)
        darkened_end = self.darken_color(original_gradient_end)
        button.configure(fg_color=(darkened_start, darkened_end))

    def on_action_button_leave(self, event, button, original_gradient_start, original_gradient_end):
        button.configure(fg_color=(original_gradient_start, original_gradient_end))

    def on_dish_click(self, dish_id, dish_name, price, img_path):
        self.selected_dish = {
            "id": dish_id,
            "name": dish_name,
            "price": price,
            "img_path": img_path
        }
        self.update_dish_info_panel()

    def update_dish_info_panel(self):
        if self.dish_info_frame is None:
            return
        for widget in self.dish_info_frame.winfo_children():
            widget.destroy()
        if self.selected_dish:
            image_label = None
            if self.selected_dish["img_path"] and os.path.exists(self.selected_dish["img_path"]):
                try:
                    image = Image.open(self.selected_dish["img_path"])
                    image = image.resize((200, 150), Image.Resampling.LANCZOS)
                    image = self.apply_rounded_corners(image, radius=15)
                    image = self.apply_gradient_overlay(image)
                    ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=(200, 150))
                    image_label = ctk.CTkLabel(master=self.dish_info_frame, image=ctk_image, text="")
                    image_label.pack(pady=(20, 10))
                except Exception as e:
                    image_label = ctk.CTkLabel(master=self.dish_info_frame, text="No Image", width=200, height=150, fg_color="gray", corner_radius=15)
                    image_label.pack(pady=(20, 10))
            else:
                image_label = ctk.CTkLabel(master=self.dish_info_frame, text="No Image", width=200, height=150, fg_color="gray", corner_radius=15)
                image_label.pack(pady=(20, 10))
            name_label = ctk.CTkLabel(self.dish_info_frame, text=self.selected_dish["name"], font=self.font_dish, text_color=self.text_color)
            name_label.pack(pady=5)
            price_label = ctk.CTkLabel(self.dish_info_frame, text=f"${self.selected_dish['price']:.2f}", font=self.font_price, text_color=self.text_color)
            price_label.pack(pady=5)
            button_frame = ctk.CTkFrame(self.dish_info_frame, fg_color="transparent")
            button_frame.pack(pady=10)
            edit_button = ctk.CTkButton(
                master=button_frame,
                text="" if self.edit_icon else "Edit",
                image=self.edit_icon,
                command=lambda: self.edit_dish(self.selected_dish["id"], self.selected_dish["name"], self.selected_dish["price"]),
                width=40,
                height=40,
                fg_color=(self.primary_color, self.primary_dark),
                corner_radius=10
            )
            edit_button.pack(side="left", padx=10)
            edit_button.bind("<Enter>", lambda event, b=edit_button: self.on_action_button_enter(event, b, self.primary_color, self.primary_dark))
            edit_button.bind("<Leave>", lambda event, b=edit_button: self.on_action_button_leave(event, b, self.primary_color, self.primary_dark))
            remove_button = ctk.CTkButton(
                master=button_frame,
                text="" if self.remove_icon else "Remove",
                image=self.remove_icon,
                command=lambda: self.remove_dish(self.selected_dish["id"]),
                width=40,
                height=40,
                fg_color=(self.delete_color, self.delete_dark),
                corner_radius=10
            )
            remove_button.pack(side="left", padx=10)
            remove_button.bind("<Enter>", lambda event, b=remove_button: self.on_action_button_enter(event, b, self.delete_color, self.delete_dark))
            remove_button.bind("<Leave>", lambda event, b=remove_button: self.on_action_button_leave(event, b, self.delete_color, self.delete_dark))
        else:
            ctk.CTkLabel(
                self.dish_info_frame,
                text="Select a dish to view details",
                font=self.font_subtitle,
                text_color=self.text_color
            ).pack(expand=True)

    def show_dishes(self):
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
            command=self.back_to_menu
        )
        back_button.pack(side="left")
        back_button.bind("<Enter>", lambda event, b=back_button: self.on_action_button_enter(event, b, self.primary_color, self.primary_dark))
        back_button.bind("<Leave>", lambda event, b=back_button: self.on_action_button_leave(event, b, self.primary_color, self.primary_dark))
        ctk.CTkLabel(
            top_bar,
            text=f"Dishes in {self.category_name}",
            font=self.font_title,
            text_color=self.header_color
        ).pack(side="left", padx=20)
        search_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=10)
        center_wrapper = ctk.CTkFrame(
            search_frame,
            fg_color="white",
            corner_radius=15,
            border_width=2,
            border_color=self.shadow_color
        )
        center_wrapper.pack(expand=True)
        self.search_entry = ctk.CTkEntry(
            center_wrapper,
            placeholder_text="Search dishes...",
            width=400,
            height=50,
            font=self.font_subtitle,
            fg_color="#F9F7F0",
            text_color=self.text_color,
            border_width=0
        )
        self.search_entry.pack(side="left", padx=(10, 5))
        self.search_entry.bind("<Return>", lambda event: self.search_dishes())
        search_button = ctk.CTkButton(
            center_wrapper,
            text="" if self.search_icon else "Search",
            image=self.search_icon,
            command=self.search_dishes,
            width=50,
            height=50,
            fg_color=(self.primary_color, self.primary_dark),
            corner_radius=10
        )
        search_button.pack(side="left", padx=(0, 10))
        search_button.bind("<Enter>", lambda event, b=search_button: self.on_action_button_enter(event, b, self.primary_color, self.primary_dark))
        search_button.bind("<Leave>", lambda event, b=search_button: self.on_action_button_leave(event, b, self.primary_color, self.primary_dark))
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.scrollable_frame = ctk.CTkScrollableFrame(content_frame, fg_color="transparent", width=1200)
        self.scrollable_frame.pack(side="left", fill="both", expand=True)
        self.dishes_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.dishes_frame.pack(fill="both", expand=True)
        if not self.all_dishes:
            try:
                from db_connection import get_dishes_by_category
                self.all_dishes = get_dishes_by_category(self.category_id)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch dishes: {e}")
                return
        self.filtered_dishes = self.all_dishes
        self.display_dishes()
        button_frame = ctk.CTkFrame(
            content_frame,
            fg_color=("white", "#F9F7F0"),
            width=300,
            corner_radius=20,
            border_width=2,
            border_color=self.shadow_color
        )
        button_frame.pack(side="right", fill="y", padx=20, pady=20)
        button_frame.pack_propagate(False)
        add_button = ctk.CTkButton(
            button_frame,
            text="Add New Dish",
            command=self.add_dish,
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
        self.dish_info_frame = ctk.CTkFrame(
            button_frame,
            fg_color="#F9F7F0",
            width=260,
            height=340,  # Increased height to accommodate vertical layout
            corner_radius=20,
            border_width=2,
            border_color=self.shadow_color
        )
        self.dish_info_frame.pack(pady=20)
        self.dish_info_frame.pack_propagate(False)
        self.update_dish_info_panel()

    def search_dishes(self):
        query = self.search_entry.get().strip().lower()
        if not query:
            self.filtered_dishes = self.all_dishes
        else:
            self.filtered_dishes = [
                dish for dish in self.all_dishes
                if query in dish[1].lower()
            ]
        self.display_dishes()

    def display_dishes(self):
        for widget in self.dishes_frame.winfo_children():
            widget.destroy()
        num_columns = 2
        num_rows = (len(self.filtered_dishes) + num_columns - 1) // num_columns
        required_height = num_rows * 260
        self.dishes_frame.configure(height=required_height)
        dish_frames = []
        for idx, (dish_id, dish_name, price, category_id, img_path) in enumerate(self.filtered_dishes):
            row = idx // num_columns
            col = idx % num_columns
            dish_frame = ctk.CTkFrame(
                self.dishes_frame,
                fg_color="#F9F7F0",
                width=550,
                height=240,
                corner_radius=20,
                border_width=2,
                border_color=self.shadow_color
            )
            dish_frame.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")
            dish_frame.grid_propagate(False)
            dish_frame.bind("<Enter>", lambda event, f=dish_frame: self.on_dish_frame_enter(event, f))
            dish_frame.bind("<Leave>", lambda event, f=dish_frame: self.on_dish_frame_leave(event, f))
            dish_frame.bind("<Button-1>", lambda event, did=dish_id, dname=dish_name, dprice=price, dimg=img_path: self.on_dish_click(did, dname, dprice, dimg))
            dish_frames.append((dish_name, dish_frame))
            image_label = None
            if img_path and os.path.exists(img_path):
                try:
                    image = Image.open(img_path)
                    image = image.resize((200, 150), Image.Resampling.LANCZOS)
                    image = self.apply_rounded_corners(image, radius=15)
                    image = self.apply_gradient_overlay(image)
                    ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=(200, 150))
                    image_label = ctk.CTkLabel(master=dish_frame, image=ctk_image, text="")
                    image_label.place(x=20, y=20)
                except Exception as e:
                    image_label = ctk.CTkLabel(master=dish_frame, text="No Image", width=200, height=150, fg_color="gray", corner_radius=15)
                    image_label.place(x=20, y=20)
            else:
                image_label = ctk.CTkLabel(master=dish_frame, text="No Image", width=200, height=150, fg_color="gray", corner_radius=15)
                image_label.place(x=20, y=20)
            name_label = ctk.CTkLabel(dish_frame, text=dish_name, font=self.font_dish, text_color=self.text_color)
            name_label.place(x=240, y=40)
            price_label = ctk.CTkLabel(dish_frame, text=f"${price:.2f}", font=self.font_price, text_color=self.text_color)
            price_label.place(x=240, y=80)
            edit_button = ctk.CTkButton(
                master=dish_frame,
                text="" if self.edit_icon else "Edit",
                image=self.edit_icon,
                command=lambda did=dish_id, dname=dish_name, dprice=price: self.edit_dish(did, dname, dprice),
                width=40,
                height=40,
                fg_color=(self.primary_color, self.primary_dark),
                corner_radius=10
            )
            edit_button.place(x=400, y=140)
            edit_button.bind("<Enter>", lambda event, b=edit_button: self.on_action_button_enter(event, b, self.primary_color, self.primary_dark))
            edit_button.bind("<Leave>", lambda event, b=edit_button: self.on_action_button_leave(event, b, self.primary_color, self.primary_dark))
            remove_button = ctk.CTkButton(
                master=dish_frame,
                text="" if self.remove_icon else "Remove",
                image=self.remove_icon,
                command=lambda did=dish_id: self.remove_dish(did),
                width=40,
                height=40,
                fg_color=(self.delete_color, self.delete_dark),
                corner_radius=10
            )
            remove_button.place(x=460, y=140)
            remove_button.bind("<Enter>", lambda event, b=remove_button: self.on_action_button_enter(event, b, self.delete_color, self.delete_dark))
            remove_button.bind("<Leave>", lambda event, b=remove_button: self.on_action_button_leave(event, b, self.delete_color, self.delete_dark))
        for i in range(num_rows):
            self.dishes_frame.grid_rowconfigure(i, weight=1, minsize=260)
        for j in range(num_columns):
            self.dishes_frame.grid_columnconfigure(j, weight=1, minsize=590)
        self.dishes_frame.grid_propagate(False)
        self.root.update()

    def add_dish(self):
        try:
            from add_dish_screen import AddDishScreen
            for widget in self.root.winfo_children():
                widget.destroy()
            AddDishScreen(self.root, self.role, self.category_id, self.category_name)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Add Dish screen: {e}")

    def get_dish_img_path(self, dish_id):
        for dish in self.all_dishes:
            if dish[0] == dish_id:
                return dish[4]
        return None

    def edit_dish(self, dish_id, dish_name, price):
        try:
            from edit_dish_screen import EditDishScreen
            img_path = self.get_dish_img_path(dish_id)
            for widget in self.root.winfo_children():
                widget.destroy()
            EditDishScreen(self.root, self.role, self.category_id, self.category_name, dish_id, dish_name, price, img_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Edit Dish screen: {e}")

    def remove_dish(self, dish_id):
        if messagebox.askyesno("Confirm", "Are you sure you want to remove this dish?"):
            try:
                from db_connection import delete_dish
                success, img_path = delete_dish(dish_id)
                if success:
                    if img_path and os.path.exists(img_path):
                        os.remove(img_path)
                    self.all_dishes = [dish for dish in self.all_dishes if dish[0] != dish_id]
                    self.filtered_dishes = self.all_dishes
                    messagebox.showinfo("Info", "Dish removed successfully!")
                    self.selected_dish = None
                    self.update_dish_info_panel()
                    self.show_dishes()
                else:
                    messagebox.showerror("Error", "Dish not found.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

    def refresh_dishes(self):
        try:
            self.all_dishes = []
            self.show_dishes()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh dishes: {e}")

    def back_to_menu(self):
        try:
            from menu_screen import MenuScreen
            for widget in self.root.winfo_children():
                widget.destroy()
            MenuScreen(self.root, self.role)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to return to menu screen: {e}")