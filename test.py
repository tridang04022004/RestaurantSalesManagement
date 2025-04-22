# create_paid_invoices_table.py
import sqlite3
from db_connection import get_db_connection

def create_paid_invoices_table():
    """Create the paid_invoices table with all fields from invoices plus invoice_id and payment_type."""
    try:
        # Connect to the database using the get_db_connection function
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create the paid_invoices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paid_invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_id INTEGER,
                total_amount REAL NOT NULL,
                timestamp TEXT NOT NULL,
                type TEXT NOT NULL DEFAULT 'dine in',
                status TEXT NOT NULL DEFAULT 'unpaid',
                invoice_id INTEGER NOT NULL,
                payment_type TEXT NOT NULL,
                FOREIGN KEY (table_id) REFERENCES tables(id),
                FOREIGN KEY (invoice_id) REFERENCES invoices(id)
            )
        ''')

        # Commit the changes and close the connection
        conn.commit()
        print("Successfully created the paid_invoices table.")
        
    except sqlite3.Error as e:
        print(f"Error creating paid_invoices table: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    create_paid_invoices_table()