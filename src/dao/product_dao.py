from dao.connection import get_connection
from datetime import datetime

def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_product(code, name, unit, price, stock, min_stock, note):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (code, name, unit, price, stock, min_stock, note) VALUES (?, ?, ?, ?, ?, ?, ?)", (code, name, unit, price, stock, min_stock, note))
    conn.commit()
    conn.close()

def update_inventory_stock(product_id, add_quantity, note="Nhập hàng mỏ"):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (add_quantity, product_id))
    cursor.execute("INSERT INTO inventory_logs (product_id, type, quantity, created_at, note) VALUES (?, 'Nhập kho', ?, ?, ?)", (product_id, add_quantity, now_str, note))
    conn.commit()
    conn.close()

def update_product(product_id, code, name, unit, price, stock, min_stock, note):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET code = ?, name = ?, unit = ?, price = ?, stock = ?, min_stock = ?, note = ? WHERE id = ?", (code, name, unit, price, stock, min_stock, note, product_id))
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
