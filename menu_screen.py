import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
import os

class MenuScreen:
    def __init__(self, root, role):
        self.root = root
        self.role = role
        self.root.title("Restaurant Management - Menu")
        self.root.geometry("1600x900")
        self.primary_color = "#9ACBD0"
        self.primary_dark = "#006A71"
        self.accent_color = "#9ACBD0"
        self.accent_dark = "#006A71"
        self.background_start = "#F2EFE7"
        self.background_end = "#E8E4D9"
        self.text_color = "#48A6A7"
        self.header_color = "#006A71"
        self.delete_color = "#FF6F61"
        self.delete_dark = "#D94F43"
        self.hover_color = "#D1E8E8"
        self.shadow_color = "#D3CFC3"
        self.font_title = ("Helvetica", 28, "bold")
        self.font_header = ("Helvetica", 18, "bold")
        self.font_medium = ("Helvetica", 16)
        self.font_button = ("Helvetica", 14, "bold")
        self.font_small = ("Helvetica", 14)
        self.font_category = ("Helvetica", 24, "bold")
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
        self.all_categories = []
        self.filtered_categories = []
        try:
            self.show_menu()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load menu screen: {e}")

    def darken_color(self, hex_color):
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = max(0, int(r * 0.8))
        g = max(0, int(g * 0.8))
        b = max(0, int(b * 0.8))
        return f"#{r:02x}{g:02x}{b:02x}"

    def on_category_enter(self, event, frame):
        frame.configure(fg_color=self.hover_color)
        for child in frame.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                for subchild in child.winfo_children():
                    if isinstance(subchild, ctk.CTkLabel) and subchild.cget("image"):
                        subchild.configure(image=subchild.cget("image"))

    def on_category_leave(self, event, frame):
        frame.configure(fg_color="#F9F7F0")

    def on_button_enter(self, event, button, original_gradient_start, original_gradient_end):
        darkened_start = self.darken_color(original_gradient_start)
        darkened_end = self.darken_color(original_gradient_end)
        button.configure(fg_color=(darkened_start, darkened_end))

    def on_button_leave(self, event, button, original_gradient_start, original_gradient_end):
        button.configure(fg_color=(original_gradient_start, original_gradient_end))

    def on_action_button_enter(self, event, button, original_gradient_start, original_gradient_end):
        darkened_start = self.darken_color(original_gradient_start)
        darkened_end = self.darken_color(original_gradient_end)
        button.configure(fg_color=(darkened_start, darkened_end))

    def on_action_button_leave(self, event, button, original_gradient_start, original_gradient_end):
        button.configure(fg_color=(original_gradient_start, original_gradient_end))

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

    def add_text_with_outline(self, image, text, font_size, text_color, outline_color, outline_thickness):
        try:
            text_image = Image.new('RGBA', image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(text_image)
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                font = ImageFont.load_default()
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            text_x = (image.width - text_width) // 2
            text_y = (image.height - text_height) // 2
            for offset_x in range(-outline_thickness, outline_thickness + 1):
                for offset_y in range(-outline_thickness, outline_thickness + 1):
                    if offset_x != 0 or offset_y != 0:
                        draw.text(
                            (text_x + offset_x, text_y + offset_y),
                            text,
                            font=font,
                            fill=outline_color
                        )
            draw.text((text_x, text_y), text, font=font, fill=text_color)
            image.paste(text_image, (0, 0), text_image)
            return image
        except Exception as e:
            return image

    def filter_categories(self, search_text):
        self.filtered_categories = [
            category for category in self.all_categories
            if search_text.lower() in category[1].lower()
        ]
        self.display_categories(self.filtered_categories)

    def display_categories(self, categories):
        for widget in self.categories_frame.winfo_children():
            widget.destroy()
        num_rows = (len(categories) + 2) // 3
        required_height = num_rows * 240
        self.categories_frame.configure(height=required_height)
        category_frames = []
        for idx, (category_id, category_name, img_path) in enumerate(categories):
            row = idx // 3
            col = idx % 3
            category_frame = ctk.CTkFrame(
                self.categories_frame,
                fg_color="#F9F7F0",
                width=400,
                height=200,
                corner_radius=15,
                border_width=2,
                border_color=self.shadow_color
            )
            category_frame.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")
            category_frame.grid_propagate(False)
            category_frames.append((category_name, category_frame))
            category_frame.bind("<Enter>", lambda event, f=category_frame: self.on_category_enter(event, f))
            category_frame.bind("<Leave>", lambda event, f=category_frame: self.on_category_leave(event, f))
            image_frame = ctk.CTkFrame(category_frame, fg_color="transparent", width=380, height=110)
            image_frame.pack(pady=(10, 0))
            image_frame.pack_propagate(False)
            image_label = None
            if img_path and os.path.exists(img_path):
                try:
                    image = Image.open(img_path)
                    image = image.resize((360, 90), Image.Resampling.LANCZOS)
                    image = self.apply_rounded_corners(image, radius=20)
                    gradient = Image.new('RGBA', image.size, (0, 0, 0, 0))
                    draw = ImageDraw.Draw(gradient)
                    for y in range(image.height):
                        alpha = int(150 * (y / image.height))
                        draw.line([(0, y), (image.width, y)], fill=(0, 0, 0, alpha))
                    image.paste(gradient, (0, 0), gradient)
                    image = self.add_text_with_outline(
                        image=image,
                        text=category_name,
                        font_size=30,
                        text_color=(255, 255, 255, 255),
                        outline_color=(30, 144, 255, 255),
                        outline_thickness=2
                    )
                    dimmed_image = ImageEnhance.Brightness(image).enhance(0.7)
                    ctk_image_normal = ctk.CTkImage(light_image=image, dark_image=image, size=(360, 90))
                    ctk_image_dimmed = ctk.CTkImage(light_image=dimmed_image, dark_image=dimmed_image, size=(360, 90))
                    image_label = ctk.CTkLabel(
                        master=image_frame,
                        image=ctk_image_normal,
                        text="",
                        width=360,
                        height=90,
                        corner_radius=10
                    )
                    image_label.place(relx=0.5, rely=0.5, anchor="center")
                    image_label.bind("<Button-1>", lambda event, cid=category_id, cname=category_name: self.show_dishes(cid, cname))
                    image_label.bind("<Enter>", lambda event, label=image_label, img=ctk_image_dimmed: label.configure(image=img))
                    image_label.bind("<Leave>", lambda event, label=image_label, img=ctk_image_normal: label.configure(image=img))
                except Exception as e:
                    image_label = ctk.CTkLabel(
                        master=image_frame,
                        text=f"{category_name}\n(Image Failed to Load)",
                        font=self.font_category,
                        width=360,
                        height=90,
                        fg_color="gray",
                        text_color="white",
                        corner_radius=10
                    )
                    image_label.place(relx=0.5, rely=0.5, anchor="center")
                    image_label.bind("<Button-1>", lambda event, cid=category_id, cname=category_name: self.show_dishes(cid, cname))
            else:
                image_label = ctk.CTkLabel(
                    master=image_frame,
                    text=f"{category_name}\n(No Image)",
                    font=self.font_category,
                    width=360,
                    height=90,
                    fg_color=self.primary_color,
                    text_color="white",
                    corner_radius=10
                )
                image_label.place(relx=0.5, rely=0.5, anchor="center")
                image_label.bind("<Button-1>", lambda event, cid=category_id, cname=category_name: self.show_dishes(cid, cname))
            button_frame = ctk.CTkFrame(category_frame, fg_color="transparent")
            button_frame.pack(pady=(0, 10))
            edit_button = ctk.CTkButton(
                master=button_frame,
                text="" if self.edit_icon else "Edit",
                image=self.edit_icon,
                command=lambda cid=category_id, cname=category_name: self.edit_category(cid, cname),
                width=40,
                height=40,
                fg_color=(self.primary_color, self.primary_dark),
                corner_radius=10
            )
            edit_button.pack(side="left", padx=5)
            edit_button.bind("<Enter>", lambda event, b=edit_button: self.on_button_enter(event, b, self.primary_color, self.primary_dark))
            edit_button.bind("<Leave>", lambda event, b=edit_button: self.on_button_leave(event, b, self.primary_color, self.primary_dark))
            remove_button = ctk.CTkButton(
                master=button_frame,
                text="" if self.remove_icon else "Remove",
                image=self.remove_icon,
                command=lambda cid=category_id: self.remove_category(cid),
                width=40,
                height=40,
                fg_color=(self.delete_color, self.delete_dark),
                corner_radius=10
            )
            remove_button.pack(side="left", padx=5)
            remove_button.bind("<Enter>", lambda event, b=remove_button: self.on_button_enter(event, b, self.delete_color, self.delete_dark))
            remove_button.bind("<Leave>", lambda event, b=remove_button: self.on_button_leave(event, b, self.delete_color, self.delete_dark))
        for i in range((len(categories) + 2) // 3):
            self.categories_frame.grid_rowconfigure(i, weight=1, minsize=240)
        for j in range(3):
            self.categories_frame.grid_columnconfigure(j, weight=1, minsize=440)
        self.root.update()

    def show_menu(self):
        main_frame = ctk.CTkFrame(self.root, fg_color=(self.background_start, self.background_end))
        main_frame.pack(fill="both", expand=True)
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        top_bar = ctk.CTkFrame(content_frame, fg_color="transparent", height=60)
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
        back_button.pack(side="left", padx=10)
        back_button.bind("<Enter>", lambda event, b=back_button: self.on_action_button_enter(event, b, self.primary_color, self.primary_dark))
        back_button.bind("<Leave>", lambda event, b=back_button: self.on_action_button_leave(event, b, self.primary_color, self.primary_dark))
        header_label = ctk.CTkLabel(
            top_bar,
            text="Menu Categories",
            font=self.font_title,
            text_color=self.header_color,
            fg_color="transparent"
        )
        header_label.pack(expand=True)
        search_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        search_frame.pack(fill="x", pady=20)
        inner_wrapper = ctk.CTkFrame(search_frame, fg_color="transparent")
        inner_wrapper.pack(expand=True)
        center_wrapper = ctk.CTkFrame(
            inner_wrapper,
            fg_color="#F9F7F0",
            corner_radius=15,
            border_width=2,
            border_color=self.shadow_color
        )
        center_wrapper.pack(side="left")
        self.search_entry = ctk.CTkEntry(
            center_wrapper,
            placeholder_text="Search categories...",
            width=450,
            height=40,
            font=self.font_medium,
            fg_color="#F9F7F0",
            text_color=self.text_color,
            border_width=0
        )
        self.search_entry.pack(side="left", padx=(10, 5))
        self.search_entry.bind("<KeyRelease>", lambda event: self.filter_categories(self.search_entry.get()))
        search_button = ctk.CTkButton(
            center_wrapper,
            text="" if self.search_icon else "Search",
            image=self.search_icon,
            command=lambda: self.filter_categories(self.search_entry.get()),
            width=40,
            height=40,
            fg_color=(self.primary_color, self.primary_dark),
            corner_radius=10
        )
        search_button.pack(side="left", padx=(0, 10))
        search_button.bind("<Enter>", lambda event, b=search_button: self.on_button_enter(event, b, self.primary_color, self.primary_dark))
        search_button.bind("<Leave>", lambda event, b=search_button: self.on_button_leave(event, b, self.primary_color, self.primary_dark))
        add_category_button = ctk.CTkButton(
            inner_wrapper,
            text="Add Category",
            command=self.add_category,
            font=self.font_medium,
            width=120,
            height=40,
            fg_color=(self.accent_color, self.accent_dark),
            text_color="black",
            corner_radius=10,
            border_width=2,
            border_color=self.accent_dark
        )
        add_category_button.pack(side="left", padx=(2, 0))
        add_category_button.bind("<Enter>", lambda event, b=add_category_button: self.on_button_enter(event, b, self.accent_color, self.accent_dark))
        add_category_button.bind("<Leave>", lambda event, b=add_category_button: self.on_button_leave(event, b, self.accent_color, self.accent_dark))
        self.scrollable_frame = ctk.CTkScrollableFrame(
            content_frame,
            fg_color="transparent",
            width=1560,
            height=650,
            corner_radius=15,
            border_width=2,
            border_color=self.shadow_color
        )
        self.scrollable_frame.pack(fill="both", expand=True)
        self.categories_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.categories_frame.pack(fill="both", expand=True)
        try:
            from db_connection import get_all_categories
            self.all_categories = get_all_categories()
            self.filtered_categories = self.all_categories.copy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch categories: {e}")
            return
        self.display_categories(self.filtered_categories)

    def show_dishes(self, category_id, category_name):
        try:
            from dishes_screen import DishesScreen
            for widget in self.root.winfo_children():
                widget.destroy()
            DishesScreen(self.root, self.role, category_id, category_name)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dishes screen: {e}")

    def add_category(self):
        try:
            from add_category_screen import AddCategoryScreen
            for widget in self.root.winfo_children():
                widget.destroy()
            AddCategoryScreen(self.root, self.role)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Add Category screen: {e}")

    def edit_category(self, category_id, category_name):
        try:
            from edit_category_screen import EditCategoryScreen
            for widget in self.root.winfo_children():
                widget.destroy()
            EditCategoryScreen(self.root, self.role, category_id, category_name)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Edit Category screen: {e}")

    def remove_category(self, category_id):
        if messagebox.askyesno("Confirm", "Are you sure you want to remove this category?"):
            try:
                from db_connection import delete_category
                success, img_path = delete_category(category_id)
                if success:
                    if img_path and os.path.exists(img_path):
                        os.remove(img_path)
                    messagebox.showinfo("Info", "Category removed successfully!")
                    self.all_categories = [cat for cat in self.all_categories if cat[0] != category_id]
                    self.filter_categories(self.search_entry.get())
                else:
                    messagebox.showerror("Error", "Category not found.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

    def refresh_menu(self):
        try:
            for widget in self.root.winfo_children():
                widget.destroy()
            self.show_menu()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh menu: {e}")

    def back_to_main(self):
        try:
            from main_screen import MainScreen
            for widget in self.root.winfo_children():
                widget.destroy()
            MainScreen(self.root, self.role)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to return to main screen: {e}")