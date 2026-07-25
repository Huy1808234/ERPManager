import sqlite3
from datetime import datetime
import config

def get_connection():
    return sqlite3.connect(config.DB_PATH)

def add_invoice(code, import_date, product_id, volume, amount, note):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO invoices (code, import_date, product_id, volume, amount, note)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (code, import_date, product_id, volume, amount, note))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_invoice(invoice_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def get_all_invoices(start_date=None, end_date=None):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = '''
        SELECT i.id, i.code, i.import_date, i.volume, i.amount, i.note, i.created_at,
               p.name as product_name
        FROM invoices i
        JOIN products p ON i.product_id = p.id
        WHERE 1=1
    '''
    params = []
    if start_date:
        query += " AND i.import_date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND i.import_date <= ?"
        params.append(end_date)
        
    query += " ORDER BY i.import_date DESC"
    
    try:
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_tax_summary(start_date=None, end_date=None):
    """
    Returns a summary of input volume (invoices) vs output volume (orders) per product.
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    inv_where = ""
    ord_where = ""
    inv_params = []
    ord_params = []
    
    if start_date:
        inv_where += " AND import_date >= ?"
        ord_where += " AND date(o.created_at) >= ?"
        inv_params.append(start_date)
        ord_params.append(start_date)
        
    if end_date:
        inv_where += " AND import_date <= ?"
        ord_where += " AND date(o.created_at) <= ?"
        inv_params.append(end_date)
        ord_params.append(end_date)
        
    query = f"""
        SELECT 
            p.id as product_id,
            p.name as product_name,
            COALESCE(inv.total_in, 0.0) as total_in,
            COALESCE(ord.total_out, 0.0) as total_out,
            (COALESCE(inv.total_in, 0.0) - COALESCE(ord.total_out, 0.0)) as diff
        FROM products p
        LEFT JOIN (
            SELECT product_id, SUM(volume) as total_in
            FROM invoices
            WHERE 1=1 {inv_where}
            GROUP BY product_id
        ) inv ON p.id = inv.product_id
        LEFT JOIN (
            SELECT oi.product_id, SUM(oi.total_volume) as total_out
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            WHERE 1=1 {ord_where}
            GROUP BY oi.product_id
        ) ord ON p.id = ord.product_id
        ORDER BY p.name
    """
    
    try:
        cursor.execute(query, inv_params + ord_params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()
