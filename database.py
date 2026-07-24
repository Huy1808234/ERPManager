"""
Database Management Module for VLXD Thống Nhất (Tân Phước)
SQLite backend with thread-safe connection and helper functions.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vlxd_thongnhat.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Danh mục Vật liệu (Products)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        unit TEXT NOT NULL,
        price REAL NOT NULL DEFAULT 0,
        stock REAL NOT NULL DEFAULT 0,
        min_stock REAL NOT NULL DEFAULT 10,
        note TEXT
    );
    """)

    # 2. Khách hàng / Nhà thầu (Customers)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        address TEXT,
        debt REAL NOT NULL DEFAULT 0,
        credit_limit REAL NOT NULL DEFAULT 50000000,
        is_contractor INTEGER NOT NULL DEFAULT 1,
        created_at TEXT
    );
    """)

    # 3. Đội xe & Tài xế (Vehicles)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plate_number TEXT UNIQUE NOT NULL,
        driver_name TEXT NOT NULL,
        phone TEXT,
        capacity_m3 REAL NOT NULL DEFAULT 2.2,
        pay_per_trip REAL NOT NULL DEFAULT 50000,
        fuel_per_trip REAL NOT NULL DEFAULT 30000,
        status TEXT NOT NULL DEFAULT 'Rảnh'
    );
    """)

    # 4. Đơn hàng (Orders)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        created_at TEXT NOT NULL,
        customer_id INTEGER,
        vehicle_id INTEGER,
        total_volume REAL NOT NULL DEFAULT 0,
        product_amount REAL NOT NULL DEFAULT 0,
        shipping_cost REAL NOT NULL DEFAULT 0,
        total_amount REAL NOT NULL DEFAULT 0,
        paid_amount REAL NOT NULL DEFAULT 0,
        debt_amount REAL NOT NULL DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'Đã hoàn thành',
        note TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(id),
        FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
    );
    """)

    # 5. Chi tiết đơn hàng (Order Items)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        volume_per_trip REAL NOT NULL DEFAULT 0,
        trips_count INTEGER NOT NULL DEFAULT 1,
        total_volume REAL NOT NULL DEFAULT 0,
        unit_price REAL NOT NULL DEFAULT 0,
        subtotal REAL NOT NULL DEFAULT 0,
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    );
    """)

    # 6. Nhật ký kho (Inventory Logs)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        type TEXT NOT NULL, -- 'Nhập kho', 'Xuất kho bán', 'Điều chỉnh'
        quantity REAL NOT NULL,
        created_at TEXT NOT NULL,
        note TEXT,
        FOREIGN KEY (product_id) REFERENCES products(id)
    );
    """)

    # 7. Sổ nợ (Debt Records)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS debt_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        order_id INTEGER,
        type TEXT NOT NULL, -- 'Ghi nợ', 'Thanh toán'
        amount REAL NOT NULL,
        balance_after REAL NOT NULL,
        created_at TEXT NOT NULL,
        note TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(id),
        FOREIGN KEY (order_id) REFERENCES orders(id)
    );
    """)

    # 8. Nhân viên (Employees)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        phone TEXT,
        position TEXT NOT NULL, -- 'Tài xế xe ben', 'Lái xe múc', 'Kế toán bán hàng', 'Bốc xếp / Bảo vệ'
        salary_type TEXT NOT NULL DEFAULT 'Lương tháng', -- 'Theo chuyến', 'Lương tháng'
        base_salary REAL NOT NULL DEFAULT 0,
        pay_per_trip REAL NOT NULL DEFAULT 50000,
        allowance REAL NOT NULL DEFAULT 0,
        created_at TEXT
    );
    """)

    # 9. Ứng lương & Phụ cấp (Salary Advances)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS salary_advances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        amount REAL NOT NULL DEFAULT 0,
        advance_date TEXT NOT NULL,
        note TEXT,
        FOREIGN KEY (employee_id) REFERENCES employees(id)
    );
    """)

    conn.commit()
    conn.close()

# --- HELPER DATABASE API FUNCTIONS ---

def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_customers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_vehicles():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vehicles ORDER BY plate_number ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_order_transaction(customer_id, vehicle_id, product_id, volume_per_trip, trips_count, unit_price, shipping_cost, paid_amount, note):
    """
    Core Order Creation Engine:
    - Calculates Total Volume = volume_per_trip * trips_count
    - Calculates Product Subtotal = Total Volume * unit_price
    - Calculates Total Amount = Product Subtotal + shipping_cost
    - Calculates Debt = Total Amount - paid_amount
    - Deducts Stock from Warehouse
    - Updates Customer Debt balance
    - Log Inventory & Debt transactions
    """
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = f"HD{datetime.now().strftime('%Y%m%d%H%M%S')}"

    total_volume = float(volume_per_trip) * int(trips_count)
    product_amount = total_volume * float(unit_price)
    total_amount = product_amount + float(shipping_cost)
    paid = float(paid_amount)
    debt = total_amount - paid

    # 1. Insert Order
    cursor.execute("""
        INSERT INTO orders (code, created_at, customer_id, vehicle_id, total_volume, product_amount, shipping_cost, total_amount, paid_amount, debt_amount, status, note)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Đã hoàn thành', ?)
    """, (code, now_str, customer_id, vehicle_id, total_volume, product_amount, shipping_cost, total_amount, paid, debt, note))
    order_id = cursor.lastrowid

    # 2. Insert Order Item
    cursor.execute("""
        INSERT INTO order_items (order_id, product_id, volume_per_trip, trips_count, total_volume, unit_price, subtotal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (order_id, product_id, volume_per_trip, trips_count, total_volume, unit_price, product_amount))

    # 3. Deduct Inventory Stock
    cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (total_volume, product_id))
    cursor.execute("""
        INSERT INTO inventory_logs (product_id, type, quantity, created_at, note)
        VALUES (?, 'Xuất kho bán', ?, ?, ?)
    """, (product_id, total_volume, now_str, f"Xuất đơn {code}"))

    # 4. Update Customer Debt & Log
    if customer_id:
        cursor.execute("SELECT debt FROM customers WHERE id = ?", (customer_id,))
        row = cursor.fetchone()
        current_debt = row['debt'] if row else 0
        new_debt = current_debt + debt
        cursor.execute("UPDATE customers SET debt = ? WHERE id = ?", (new_debt, customer_id))

        if debt != 0:
            cursor.execute("""
                INSERT INTO debt_records (customer_id, order_id, type, amount, balance_after, created_at, note)
                VALUES (?, ?, 'Ghi nợ', ?, ?, ?, ?)
            """, (customer_id, order_id, debt, new_debt, now_str, f"Ghi nợ đơn hàng {code}"))

    conn.commit()
    conn.close()
    return code, total_volume, total_amount, debt

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

    cursor.execute("""
        INSERT INTO debt_records (customer_id, order_id, type, amount, balance_after, created_at, note)
        VALUES (?, NULL, 'Thanh toán', ?, ?, ?, ?)
    """, (customer_id, amount, new_debt, now_str, note))

    conn.commit()
    conn.close()
    return True

def add_product(code, name, unit, price, stock, min_stock, note):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (code, name, unit, price, stock, min_stock, note)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (code, name, unit, price, stock, min_stock, note))
    conn.commit()
    conn.close()

def add_customer(name, phone, address, credit_limit, is_contractor):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO customers (name, phone, address, debt, credit_limit, is_contractor, created_at)
        VALUES (?, ?, ?, 0, ?, ?, ?)
    """, (name, phone, address, credit_limit, is_contractor, now_str))
    conn.commit()
    conn.close()

def add_vehicle(plate_number, driver_name, phone, capacity_m3, pay_per_trip, fuel_per_trip):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO vehicles (plate_number, driver_name, phone, capacity_m3, pay_per_trip, fuel_per_trip, status)
        VALUES (?, ?, ?, ?, ?, ?, 'Rảnh')
    """, (plate_number, driver_name, phone, capacity_m3, pay_per_trip, fuel_per_trip))
    conn.commit()
    conn.close()

def update_inventory_stock(product_id, add_quantity, note="Nhập hàng mỏ"):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (add_quantity, product_id))
    cursor.execute("""
        INSERT INTO inventory_logs (product_id, type, quantity, created_at, note)
        VALUES (?, 'Nhập kho', ?, ?, ?)
    """, (product_id, add_quantity, now_str, note))
    conn.commit()
    conn.close()

def update_product(product_id, code, name, unit, price, stock, min_stock, note):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products
        SET code = ?, name = ?, unit = ?, price = ?, stock = ?, min_stock = ?, note = ?
        WHERE id = ?
    """, (code, name, unit, price, stock, min_stock, note, product_id))
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

def update_customer(customer_id, name, phone, address, credit_limit, is_contractor):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE customers
        SET name = ?, phone = ?, address = ?, credit_limit = ?, is_contractor = ?
        WHERE id = ?
    """, (name, phone, address, credit_limit, is_contractor, customer_id))
    conn.commit()
    conn.close()

def delete_customer(customer_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM debt_records WHERE customer_id = ?", (customer_id,))
    cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
    conn.commit()
    conn.close()

def update_vehicle(vehicle_id, plate_number, driver_name, phone, capacity_m3, pay_per_trip, fuel_per_trip):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE vehicles
        SET plate_number = ?, driver_name = ?, phone = ?, capacity_m3 = ?, pay_per_trip = ?, fuel_per_trip = ?
        WHERE id = ?
    """, (plate_number, driver_name, phone, capacity_m3, pay_per_trip, fuel_per_trip, vehicle_id))
    conn.commit()
    conn.close()

def delete_vehicle(vehicle_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vehicles WHERE id = ?", (vehicle_id,))
    conn.commit()
    conn.close()

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

    # Reverse stock deduction
    cursor.execute("SELECT product_id, total_volume FROM order_items WHERE order_id = ?", (order_id,))
    items = cursor.fetchall()
    for item in items:
        cursor.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (item['total_volume'], item['product_id']))

    # Reverse customer debt
    if customer_id and debt_amount != 0:
        cursor.execute("UPDATE customers SET debt = MAX(0, debt - ?) WHERE id = ?", (debt_amount, customer_id))

    cursor.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
    cursor.execute("DELETE FROM debt_records WHERE order_id = ?", (order_id,))
    cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
    return True

def get_orders_list():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.*, c.name as customer_name, v.plate_number, v.driver_name, p.name as product_name
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.id
        LEFT JOIN vehicles v ON o.vehicle_id = v.id
        LEFT JOIN order_items oi ON o.id = oi.order_id
        LEFT JOIN products p ON oi.product_id = p.id
        ORDER BY o.id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_driver_trip_summary():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT v.plate_number, v.driver_name, v.pay_per_trip, v.fuel_per_trip,
               COALESCE(SUM(oi.trips_count), 0) as total_trips,
               COALESCE(SUM(oi.total_volume), 0) as total_volume_delivered
        FROM vehicles v
        LEFT JOIN orders o ON v.id = o.vehicle_id
        LEFT JOIN order_items oi ON o.id = oi.order_id
        GROUP BY v.id
        ORDER BY total_trips DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_employees():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_employee(code, name, phone, position, salary_type, base_salary, pay_per_trip, allowance):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO employees (code, name, phone, position, salary_type, base_salary, pay_per_trip, allowance, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (code, name, phone, position, salary_type, base_salary, pay_per_trip, allowance, now_str))
    conn.commit()
    conn.close()

def update_employee(emp_id, code, name, phone, position, salary_type, base_salary, pay_per_trip, allowance):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE employees
        SET code = ?, name = ?, phone = ?, position = ?, salary_type = ?, base_salary = ?, pay_per_trip = ?, allowance = ?
        WHERE id = ?
    """, (code, name, phone, position, salary_type, base_salary, pay_per_trip, allowance, emp_id))
    conn.commit()
    conn.close()

def delete_employee(emp_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM salary_advances WHERE employee_id = ?", (emp_id,))
    cursor.execute("DELETE FROM employees WHERE id = ?", (emp_id,))
    conn.commit()
    conn.close()

def record_salary_advance(employee_id, amount, note="Tạm ứng lương"):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO salary_advances (employee_id, amount, advance_date, note)
        VALUES (?, ?, ?, ?)
    """, (employee_id, amount, now_str, note))
    conn.commit()
    conn.close()

def get_payroll_summary():
    conn = get_connection()
    cursor = conn.cursor()

    employees = [dict(r) for r in cursor.execute("SELECT * FROM employees ORDER BY id ASC").fetchall()]
    payroll_data = []

    for emp in employees:
        emp_id = emp['id']
        emp_name = emp['name']
        salary_type = emp['salary_type']

        trips_count = 0
        if salary_type == 'Theo chuyến':
            cursor.execute("""
                SELECT COALESCE(SUM(oi.trips_count), 0) as trips
                FROM orders o
                JOIN vehicles v ON o.vehicle_id = v.id
                JOIN order_items oi ON o.id = oi.order_id
                WHERE v.driver_name LIKE ?
            """, (f"%{emp_name}%",))
            row = cursor.fetchone()
            trips_count = row['trips'] if row else 0

        trip_pay = trips_count * emp['pay_per_trip'] if salary_type == 'Theo chuyến' else 0
        gross_salary = emp['base_salary'] + trip_pay + emp['allowance']

        cursor.execute("SELECT COALESCE(SUM(amount), 0) as total_advance FROM salary_advances WHERE employee_id = ?", (emp_id,))
        adv_row = cursor.fetchone()
        advances = adv_row['total_advance'] if adv_row else 0

        net_salary = max(0, gross_salary - advances)

        payroll_data.append({
            'id': emp_id,
            'code': emp['code'],
            'name': emp['name'],
            'position': emp['position'],
            'salary_type': salary_type,
            'base_salary': emp['base_salary'],
            'pay_per_trip': emp['pay_per_trip'],
            'trips_count': trips_count,
            'trip_pay': trip_pay,
            'allowance': emp['allowance'],
            'gross_salary': gross_salary,
            'advances': advances,
            'net_salary': net_salary,
            'phone': emp['phone'] or ""
        })

    conn.close()
    return payroll_data

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
