from dao.connection import get_connection
from datetime import datetime

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
    cursor.execute("INSERT INTO employees (code, name, phone, position, salary_type, base_salary, pay_per_trip, allowance, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (code, name, phone, position, salary_type, base_salary, pay_per_trip, allowance, now_str))
    conn.commit()
    conn.close()

def update_employee(emp_id, code, name, phone, position, salary_type, base_salary, pay_per_trip, allowance):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE employees SET code = ?, name = ?, phone = ?, position = ?, salary_type = ?, base_salary = ?, pay_per_trip = ?, allowance = ? WHERE id = ?", (code, name, phone, position, salary_type, base_salary, pay_per_trip, allowance, emp_id))
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
    cursor.execute("INSERT INTO salary_advances (employee_id, amount, advance_date, note) VALUES (?, ?, ?, ?)", (employee_id, amount, now_str, note))
    conn.commit()
    conn.close()

def get_payroll_summary():
    conn = get_connection()
    cursor = conn.cursor()
    query = """
    SELECT 
        e.id, e.code, e.name, e.position, e.salary_type, e.base_salary, e.pay_per_trip, e.allowance, e.phone,
        COALESCE(trip_data.total_trips, 0) as trips_count,
        COALESCE(adv_data.total_advance, 0) as advances
    FROM employees e
    LEFT JOIN (
        SELECT v.driver_name, SUM(oi.trips_count) as total_trips
        FROM vehicles v
        JOIN orders o ON v.id = o.vehicle_id
        JOIN order_items oi ON o.id = oi.order_id
        GROUP BY v.driver_name
    ) trip_data ON e.salary_type = 'Theo chuyến' AND trip_data.driver_name LIKE '%' || e.name || '%'
    LEFT JOIN (
        SELECT employee_id, SUM(amount) as total_advance
        FROM salary_advances
        GROUP BY employee_id
    ) adv_data ON e.id = adv_data.employee_id
    ORDER BY e.id ASC
    """
    rows = cursor.execute(query).fetchall()
    payroll_data = []
    for row in rows:
        emp = dict(row)
        salary_type = emp['salary_type']
        trips_count = emp['trips_count'] if salary_type == 'Theo chuyến' else 0
        trip_pay = trips_count * emp['pay_per_trip'] if salary_type == 'Theo chuyến' else 0
        gross_salary = emp['base_salary'] + trip_pay + emp['allowance']
        advances = emp['advances']
        net_salary = max(0, gross_salary - advances)
        emp['trip_pay'] = trip_pay
        emp['gross_salary'] = gross_salary
        emp['net_salary'] = net_salary
        emp['phone'] = emp['phone'] or ""
        payroll_data.append(emp)
    conn.close()
    return payroll_data
