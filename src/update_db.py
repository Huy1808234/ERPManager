import sqlite3
import os

DB_FILE = "vlxd_thongnhat.db"

def update_database():
    if not os.path.exists(DB_FILE):
        print(f"Database {DB_FILE} not found. Cannot update.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        print("Creating 'invoices' table if not exists...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                import_date TEXT NOT NULL,
                product_id INTEGER NOT NULL,
                volume REAL NOT NULL,
                amount REAL NOT NULL,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        conn.commit()
        print("Database updated successfully.")
    except Exception as e:
        print(f"Error updating database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_database()
