import sqlite3
import config

def get_connection():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE NOT NULL, name TEXT NOT NULL, unit TEXT NOT NULL, price REAL NOT NULL DEFAULT 0, stock REAL NOT NULL DEFAULT 0, min_stock REAL NOT NULL DEFAULT 10, note TEXT);''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, phone TEXT, address TEXT, debt REAL NOT NULL DEFAULT 0, credit_limit REAL NOT NULL DEFAULT 50000000, is_contractor INTEGER NOT NULL DEFAULT 1, created_at TEXT);''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS vehicles (id INTEGER PRIMARY KEY AUTOINCREMENT, plate_number TEXT UNIQUE NOT NULL, driver_name TEXT NOT NULL, phone TEXT, capacity_m3 REAL NOT NULL DEFAULT 2.2, pay_per_trip REAL NOT NULL DEFAULT 50000, fuel_per_trip REAL NOT NULL DEFAULT 30000, status TEXT NOT NULL DEFAULT 'Rảnh');''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE NOT NULL, created_at TEXT NOT NULL, customer_id INTEGER, vehicle_id INTEGER, total_volume REAL NOT NULL DEFAULT 0, product_amount REAL NOT NULL DEFAULT 0, shipping_cost REAL NOT NULL DEFAULT 0, total_amount REAL NOT NULL DEFAULT 0, paid_amount REAL NOT NULL DEFAULT 0, debt_amount REAL NOT NULL DEFAULT 0, status TEXT NOT NULL DEFAULT 'Đã hoàn thành', note TEXT, FOREIGN KEY (customer_id) REFERENCES customers(id), FOREIGN KEY (vehicle_id) REFERENCES vehicles(id));''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS order_items (id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER NOT NULL, product_id INTEGER NOT NULL, volume_per_trip REAL NOT NULL DEFAULT 0, trips_count INTEGER NOT NULL DEFAULT 1, total_volume REAL NOT NULL DEFAULT 0, unit_price REAL NOT NULL DEFAULT 0, subtotal REAL NOT NULL DEFAULT 0, FOREIGN KEY (order_id) REFERENCES orders(id), FOREIGN KEY (product_id) REFERENCES products(id));''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER NOT NULL, type TEXT NOT NULL, quantity REAL NOT NULL, created_at TEXT NOT NULL, note TEXT, FOREIGN KEY (product_id) REFERENCES products(id));''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS debt_records (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_id INTEGER NOT NULL, order_id INTEGER, type TEXT NOT NULL, amount REAL NOT NULL, balance_after REAL NOT NULL, created_at TEXT NOT NULL, note TEXT, FOREIGN KEY (customer_id) REFERENCES customers(id), FOREIGN KEY (order_id) REFERENCES orders(id));''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS employees (id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE NOT NULL, name TEXT NOT NULL, phone TEXT, position TEXT NOT NULL, salary_type TEXT NOT NULL DEFAULT 'Lương tháng', base_salary REAL NOT NULL DEFAULT 0, pay_per_trip REAL NOT NULL DEFAULT 50000, allowance REAL NOT NULL DEFAULT 0, created_at TEXT);''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS salary_advances (id INTEGER PRIMARY KEY AUTOINCREMENT, employee_id INTEGER NOT NULL, amount REAL NOT NULL DEFAULT 0, advance_date TEXT NOT NULL, note TEXT, FOREIGN KEY (employee_id) REFERENCES employees(id));''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS invoices (id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT NOT NULL, import_date TEXT NOT NULL, product_id INTEGER, volume REAL NOT NULL DEFAULT 0, amount REAL NOT NULL, note TEXT, category TEXT DEFAULT 'Vật liệu', vat_amount REAL DEFAULT 0, seller_tax_code TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (product_id) REFERENCES products (id));''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS db_metadata (version INTEGER)''')
    cursor.execute('''SELECT COUNT(*) FROM db_metadata''')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''INSERT INTO db_metadata (version) VALUES (1)''')
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_vehicle ON orders(vehicle_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items(product_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_product ON inventory_logs(product_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_debt_customer ON debt_records(customer_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_debt_order ON debt_records(order_id);")
    
    conn.commit()
    conn.close()
