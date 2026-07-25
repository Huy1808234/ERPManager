from dao.connection import get_connection
from datetime import datetime

def get_all_customers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def record_debt_payment(customer_id, payment_amount, note="Thanh toán tiền nợ"):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("SELECT debt FROM customers WHERE id = ?", (customer_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
    current_debt = row['debt']
    amount = float(payment_amount)
    new_debt = current_debt - amount
    cursor.execute("UPDATE customers SET debt = ? WHERE id = ?", (new_debt, customer_id))
    cursor.execute("INSERT INTO debt_records (customer_id, order_id, type, amount, balance_after, created_at, note) VALUES (?, NULL, 'Thanh toán', ?, ?, ?, ?)", (customer_id, amount, new_debt, now_str, note))
    conn.commit()
    conn.close()
    return True

def add_customer(name, phone, address, credit_limit, is_contractor):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO customers (name, phone, address, debt, credit_limit, is_contractor, created_at) VALUES (?, ?, ?, 0, ?, ?, ?)", (name, phone, address, credit_limit, is_contractor, now_str))
    conn.commit()
    conn.close()

def update_customer(customer_id, name, phone, address, credit_limit, is_contractor):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE customers SET name = ?, phone = ?, address = ?, credit_limit = ?, is_contractor = ? WHERE id = ?", (name, phone, address, credit_limit, is_contractor, customer_id))
    conn.commit()
    conn.close()

def delete_customer(customer_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM debt_records WHERE customer_id = ?", (customer_id,))
    cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
    conn.commit()
    conn.close()
