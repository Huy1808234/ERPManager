from dao.connection import get_connection
from datetime import datetime

def create_order_transaction(customer_id, vehicle_id, product_id, volume_per_trip, trips_count, unit_price, shipping_cost, paid_amount, note):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = f"HD{datetime.now().strftime('%Y%m%d%H%M%S')}"
    total_volume = float(volume_per_trip) * int(trips_count)
    product_amount = total_volume * float(unit_price)
    total_amount = product_amount + float(shipping_cost)
    paid = float(paid_amount)
    debt = total_amount - paid

    cursor.execute("INSERT INTO orders (code, created_at, customer_id, vehicle_id, total_volume, product_amount, shipping_cost, total_amount, paid_amount, debt_amount, status, note) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Đã hoàn thành', ?)", (code, now_str, customer_id, vehicle_id, total_volume, product_amount, shipping_cost, total_amount, paid, debt, note))
    order_id = cursor.lastrowid
    cursor.execute("INSERT INTO order_items (order_id, product_id, volume_per_trip, trips_count, total_volume, unit_price, subtotal) VALUES (?, ?, ?, ?, ?, ?, ?)", (order_id, product_id, volume_per_trip, trips_count, total_volume, unit_price, product_amount))
    cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (total_volume, product_id))
    cursor.execute("INSERT INTO inventory_logs (product_id, type, quantity, created_at, note) VALUES (?, 'Xuất kho bán', ?, ?, ?)", (product_id, total_volume, now_str, f"Xuất đơn {code}"))
    if customer_id:
        cursor.execute("SELECT debt FROM customers WHERE id = ?", (customer_id,))
        row = cursor.fetchone()
        current_debt = row['debt'] if row else 0
        new_debt = current_debt + debt
        cursor.execute("UPDATE customers SET debt = ? WHERE id = ?", (new_debt, customer_id))
        if debt != 0:
            cursor.execute("INSERT INTO debt_records (customer_id, order_id, type, amount, balance_after, created_at, note) VALUES (?, ?, 'Ghi nợ', ?, ?, ?, ?)", (customer_id, order_id, debt, new_debt, now_str, f"Ghi nợ đơn hàng {code}"))
    conn.commit()
    conn.close()
    return code, total_volume, total_amount, debt

def delete_order(order_code):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE code = ?", (order_code,))
    order = cursor.fetchone()
    if not order:
        conn.close()
        return False
    order_id = order['id']
    customer_id = order['customer_id']
    debt_amount = order['debt_amount']
    cursor.execute("SELECT product_id, total_volume FROM order_items WHERE order_id = ?", (order_id,))
    items = cursor.fetchall()
    for item in items:
        cursor.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (item['total_volume'], item['product_id']))
    if customer_id and debt_amount != 0:
        cursor.execute("UPDATE customers SET debt = MAX(0, debt - ?) WHERE id = ?", (debt_amount, customer_id))
    cursor.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
    cursor.execute("DELETE FROM debt_records WHERE order_id = ?", (order_id,))
    cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
    return True

def get_orders_list(search_query=None, start_date=None, end_date=None, limit=1000):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT o.*, c.name as customer_name, v.plate_number, v.driver_name, p.name as product_name
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.id
        LEFT JOIN vehicles v ON o.vehicle_id = v.id
        LEFT JOIN order_items oi ON o.id = oi.order_id
        LEFT JOIN products p ON oi.product_id = p.id
        WHERE 1=1
    """
    params = []
    if search_query:
        query += " AND (c.name LIKE ? OR p.name LIKE ? OR o.code LIKE ? OR v.driver_name LIKE ?)"
        like_q = f"%{search_query}%"
        params.extend([like_q, like_q, like_q, like_q])
    if start_date:
        query += " AND o.created_at >= ?"
        params.append(start_date + " 00:00:00")
    if end_date:
        query += " AND o.created_at <= ?"
        params.append(end_date + " 23:59:59")
    query += " ORDER BY o.id DESC LIMIT ?"
    params.append(limit)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_invoice_balance_report(start_date=None, end_date=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT p.code, p.name, p.unit,
            SUM(CASE WHEN i.type = 'Nhập kho' THEN i.quantity ELSE 0 END) as total_nhap,
            SUM(CASE WHEN i.type = 'Xuất kho bán' THEN i.quantity ELSE 0 END) as total_xuat
        FROM products p
        LEFT JOIN inventory_logs i ON p.id = i.product_id
    """
    params = []
    if start_date:
        query += " AND i.created_at >= ?"
        params.append(start_date + " 00:00:00")
    if end_date:
        query += " AND i.created_at <= ?"
        params.append(end_date + " 23:59:59")
        
    query += " GROUP BY p.id"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    report = []
    for row in rows:
        r = dict(row)
        nhap = r['total_nhap'] or 0
        xuat = r['total_xuat'] or 0
        r['total_nhap'] = nhap
        r['total_xuat'] = xuat
        r['chenh_lech'] = xuat - nhap
        report.append(r)
    return report
