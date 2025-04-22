# db_connection.py
import sqlite3
import os

def get_db_connection():
    try:
        conn = sqlite3.connect('restaurant.db')
        return conn
    except sqlite3.Error as e:
        raise Exception(f"Failed to connect to database: {e}")

def update_table_status(table_id, conn=None):
    """Update the status of a table based on unpaid 'dine in' invoices."""
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True

    cursor = conn.cursor()
    # Check if there are any unpaid 'dine in' invoices for this table
    cursor.execute("SELECT COUNT(*) FROM invoices WHERE table_id = ? AND type = 'dine in' AND status = 'unpaid'", (table_id,))
    unpaid_count = cursor.fetchone()[0]

    # Update the table status
    new_status = "in_use" if unpaid_count > 0 else "empty"  # Changed 'in_used' to 'in_use'
    cursor.execute("UPDATE tables SET status = ? WHERE id = ?", (new_status, table_id))
    print(f"Updated table {table_id} status to {new_status} based on {unpaid_count} unpaid 'dine in' invoices")

    if close_conn:
        conn.commit()
        conn.close()

def initialize_db():
    """Initialize the database with necessary tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    # Create categories table with img_path column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            img_path TEXT
        )
    ''')

    # Create dishes table with img_path column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dishes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category_id INTEGER,
            img_path TEXT,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    ''')

    # Create tables table with table_number (INT) and status (TEXT)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'empty'  -- 'empty', 'in_use', or 'reserved'
        )
    ''')

    # Create invoices table with type and status columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_id INTEGER,
            total_amount REAL NOT NULL,
            timestamp TEXT NOT NULL,
            type TEXT NOT NULL DEFAULT 'dine in',  -- 'dine in', 'take away', or 'delivery'
            status TEXT NOT NULL DEFAULT 'unpaid',  -- 'unpaid' or 'paid'
            FOREIGN KEY (table_id) REFERENCES tables(id)
        )
    ''')

    # Create invoice_items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER,
            dish_id INTEGER,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (invoice_id) REFERENCES invoices(id),
            FOREIGN KEY (dish_id) REFERENCES dishes(id)
        )
    ''')

    # Insert default admin user if not exists
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", "admin123", "admin"))
    
    # Create catimg folder if it doesn't exist
    if not os.path.exists("catimg"):
        os.makedirs("catimg")

    # Create img folder for dishes if it doesn't exist
    if not os.path.exists("img"):
        os.makedirs("img")

    # Insert some default categories if the table is empty (without images for now)
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        default_categories = [("Appetizers", None), ("Main Courses", None), ("Desserts", None), ("Beverages", None)]
        cursor.executemany("INSERT INTO categories (name, img_path) VALUES (?, ?)", default_categories)

    # Insert some default tables if the table is empty
    cursor.execute("SELECT COUNT(*) FROM tables")
    if cursor.fetchone()[0] == 0:
        default_tables = [(1, "empty"), (2, "empty"), (3, "reserved")]
        cursor.executemany("INSERT INTO tables (table_number, status) VALUES (?, ?)", default_tables)

    # Insert some default invoices if the table is empty
    cursor.execute("SELECT COUNT(*) FROM invoices")
    if cursor.fetchone()[0] == 0:
        default_invoices = [
            (1, 50.00, "2025-04-06 12:00:00", "dine in", "unpaid"),
            (2, 30.00, "2025-04-06 12:30:00", "take away", "unpaid"),
            (3, 45.00, "2025-04-06 13:00:00", "delivery", "unpaid"),
            (1, 60.00, "2025-04-06 13:30:00", "dine in", "paid"),
            (2, 25.00, "2025-04-06 14:00:00", "take away", "unpaid")
        ]
        cursor.executemany("INSERT INTO invoices (table_id, total_amount, timestamp, type, status) VALUES (?, ?, ?, ?, ?)", default_invoices)

        # Update table statuses based on unpaid 'dine in' invoices
        cursor.execute("SELECT DISTINCT table_id FROM invoices WHERE type = 'dine in'")
        table_ids = [row[0] for row in cursor.fetchall()]
        for table_id in table_ids:
            update_table_status(table_id, conn)

    conn.commit()
    conn.close()

def verify_login(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def add_staff(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'staff')", (username, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False
    except sqlite3.Error as e:
        conn.close()
        raise Exception(f"Database error while adding staff: {e}")

def get_all_staff():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password FROM users WHERE role = 'staff'")
    staff = cursor.fetchall()
    conn.close()
    return staff

def update_staff(staff_id, username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET username = ?, password = ? WHERE id = ? AND role = 'staff'", (username, password, staff_id))
        if cursor.rowcount == 0:
            conn.close()
            return False
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False
    except sqlite3.Error as e:
        conn.close()
        raise Exception(f"Database error while updating staff: {e}")

def delete_staff(staff_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ? AND role = 'staff'", (staff_id,))
    if cursor.rowcount == 0:
        conn.close()
        return False
    conn.commit()
    conn.close()
    return True

def get_all_categories():
    """Returns a list of all categories (id, name, img_path)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, img_path FROM categories")
    categories = cursor.fetchall()
    conn.close()
    return categories

def add_category(name, img_path=None):
    """Adds a new category with an optional image path. Returns True if successful, False if name exists."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO categories (name, img_path) VALUES (?, ?)", (name, img_path))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False
    except sqlite3.Error as e:
        conn.close()
        raise Exception(f"Database error while adding category: {e}")

def update_category(category_id, name, img_path=None):
    """Updates a category's name and image path. Returns True if successful, False if name exists or not found."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE categories SET name = ?, img_path = ? WHERE id = ?", (name, img_path, category_id))
        if cursor.rowcount == 0:
            conn.close()
            return False
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False
    except sqlite3.Error as e:
        conn.close()
        raise Exception(f"Database error while updating category: {e}")

def delete_category(category_id):
    """Deletes a category by ID and returns its img_path if it exists. Returns (True, img_path) if successful, (False, None) if not found."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT img_path FROM categories WHERE id = ?", (category_id,))
    result = cursor.fetchone()
    img_path = result[0] if result else None
    cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    if cursor.rowcount == 0:
        conn.close()
        return False, None
    conn.commit()
    conn.close()
    return True, img_path

def get_dishes_by_category(category_id):
    """Returns a list of all dishes in a category (id, name, price, category_id, img_path)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, category_id, img_path FROM dishes WHERE category_id = ?", (category_id,))
    dishes = cursor.fetchall()
    conn.close()
    return dishes

def add_dish(name, price, category_id, img_path=None):
    """Adds a new dish with an optional image path. Returns the new dish ID if successful."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO dishes (name, price, category_id, img_path) VALUES (?, ?, ?, ?)",
                       (name, price, category_id, img_path))
        dish_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return dish_id
    except sqlite3.Error as e:
        conn.close()
        raise Exception(f"Database error while adding dish: {e}")

def update_dish(dish_id, name, price, category_id, img_path):
    """Update an existing dish in the database and return the old image path."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Get the current image path to return it (for deletion if needed)
        cursor.execute("SELECT img_path FROM dishes WHERE id = ?", (dish_id,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            return False, None
        old_img_path = result[0]

        # Update the dish with the new values
        cursor.execute(
            "UPDATE dishes SET name = ?, price = ?, category_id = ?, img_path = ? WHERE id = ?",
            (name, price, category_id, img_path, dish_id)
        )
        if cursor.rowcount == 0:
            conn.close()
            return False, None
        conn.commit()
        conn.close()
        return True, old_img_path
    except sqlite3.Error as e:
        print(f"Error updating dish: {e}")
        conn.close()
        return False, None

def delete_dish(dish_id):
    """Deletes a dish by ID and returns its img_path if it exists. Returns (True, img_path) if successful, (False, None) if not found."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT img_path FROM dishes WHERE id = ?", (dish_id,))
    result = cursor.fetchone()
    img_path = result[0] if result else None
    cursor.execute("DELETE FROM dishes WHERE id = ?", (dish_id,))
    if cursor.rowcount == 0:
        conn.close()
        return False, None
    conn.commit()
    conn.close()
    return True, img_path

def get_all_tables():
    """Returns a list of all tables (id, table_number, status)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, table_number, status FROM tables")
    tables = cursor.fetchall()
    conn.close()
    return tables

def add_table(table_number, status="empty"):
    """Adds a new table with the given table number and status. Returns True if successful."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO tables (table_number, status) VALUES (?, ?)", (table_number, status))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        conn.close()
        raise Exception(f"Database error while adding table: {e}")

def update_table(table_id, table_number, status):
    """Updates a table's table number and status. Returns True if successful, False if not found."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE tables SET table_number = ?, status = ? WHERE id = ?", (table_number, status, table_id))
        if cursor.rowcount == 0:
            conn.close()
            return False
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        conn.close()
        raise Exception(f"Database error while updating table: {e}")

def delete_table(table_id):
    """Deletes a table by ID. Returns True if successful, False if not found."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tables WHERE id = ?", (table_id,))
    if cursor.rowcount == 0:
        conn.close()
        return False
    conn.commit()
    conn.close()
    return True

# Initialize the database on import
initialize_db()