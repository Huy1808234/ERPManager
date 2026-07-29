import sqlite3
from dao.connection import get_connection

def run_migrations():
    """
    Checks the current database version and applies any pending migrations.
    This ensures that when the app is updated with a new schema, 
    the client's local database is automatically updated without losing data.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT version FROM db_metadata LIMIT 1")
        row = cursor.fetchone()
        current_version = row['version'] if row else 1
    except sqlite3.OperationalError:
        # If db_metadata doesn't exist for some reason, fallback to version 1
        current_version = 1
        
    print(f"[Migration] Current Database Version: {current_version}")
    
    # ---------------------------------------------------------
    # Migration V2: Add category, vat_amount, seller_tax_code to invoices
    if current_version < 2:
        print("[Migration] Upgrading to Version 2 (Expense Invoices & VAT Deduction)...")
        try:
            # Check existing columns to prevent errors if already migrated
            cursor.execute("PRAGMA table_info(invoices)")
            cols = [col['name'] for col in cursor.fetchall()]
            
            if 'category' not in cols:
                cursor.execute("ALTER TABLE invoices ADD COLUMN category TEXT DEFAULT 'Vật liệu'")
            if 'vat_amount' not in cols:
                cursor.execute("ALTER TABLE invoices ADD COLUMN vat_amount REAL DEFAULT 0.0")
            if 'seller_tax_code' not in cols:
                cursor.execute("ALTER TABLE invoices ADD COLUMN seller_tax_code TEXT")
                
            cursor.execute("UPDATE db_metadata SET version = 2")
            current_version = 2
            print("[Migration] Successfully upgraded to Version 2!")
        except Exception as e:
            print(f"[Migration] Error upgrading to V2: {e}")
            conn.rollback()
            raise
    # ---------------------------------------------------------

    conn.commit()
    conn.close()
    
if __name__ == "__main__":
    run_migrations()
