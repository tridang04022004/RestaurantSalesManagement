import sqlite3

def create_database():
    # Connect to SQLite database (creates 'restaurant.db' if it doesn't exist)
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()

    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'staff'))
        )
    ''')

    # Create Dish_Categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dish_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    # Create Dishes table (with foreign key to dish_categories)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dishes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (category_id) REFERENCES dish_categories(id)
        )
    ''')

    # Create Tables table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number INTEGER NOT NULL UNIQUE,
            status TEXT NOT NULL CHECK(status IN ('empty', 'in_use', 'reserved'))
        )
    ''')

    # Create Invoices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_id INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (table_id) REFERENCES tables(id)
        )
    ''')

    # Create Invoice_Items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            dish_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (invoice_id) REFERENCES invoices(id),
            FOREIGN KEY (dish_id) REFERENCES dishes(id)
        )
    ''')

    # Insert default admin user (username: admin, password: admin123)
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password, role)
        VALUES (?, ?, ?)
    ''', ('admin', 'admin123', 'admin'))

    # Insert sample dish categories
    sample_categories = [
        ('Pizza',),
        ('Salad',),
        ('Pasta',),
        ('Drinks',)
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO dish_categories (name)
        VALUES (?)
    ''', sample_categories)

    # Insert sample dishes (linked to category IDs)
    sample_dishes = [
        ('Margherita Pizza', 1, 12.99),  # Category 1 = Pizza
        ('Pepperoni Pizza', 1, 14.99),   # Category 1 = Pizza
        ('Caesar Salad', 2, 8.99),       # Category 2 = Salad
        ('Spaghetti', 3, 11.99),         # Category 3 = Pasta
        ('Coke', 4, 2.99)                # Category 4 = Drinks
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO dishes (name, category_id, price)
        VALUES (?, ?, ?)
    ''', sample_dishes)

    # Insert sample tables (e.g., 10 tables)
    sample_tables = [(i, 'empty') for i in range(1, 11)]
    cursor.executemany('''
        INSERT OR IGNORE INTO tables (table_number, status)
        VALUES (?, ?)
    ''', sample_tables)

    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("Database 'restaurant.db' created successfully with initial data.")

create_database()