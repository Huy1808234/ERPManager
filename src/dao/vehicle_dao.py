from dao.connection import get_connection

def get_all_vehicles():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vehicles ORDER BY plate_number ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_vehicle(plate_number, driver_name, phone, capacity_m3, pay_per_trip, fuel_per_trip):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO vehicles (plate_number, driver_name, phone, capacity_m3, pay_per_trip, fuel_per_trip, status) VALUES (?, ?, ?, ?, ?, ?, 'Rảnh')", (plate_number, driver_name, phone, capacity_m3, pay_per_trip, fuel_per_trip))
    conn.commit()
    conn.close()

def update_vehicle(vehicle_id, plate_number, driver_name, phone, capacity_m3, pay_per_trip, fuel_per_trip):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE vehicles SET plate_number = ?, driver_name = ?, phone = ?, capacity_m3 = ?, pay_per_trip = ?, fuel_per_trip = ? WHERE id = ?", (plate_number, driver_name, phone, capacity_m3, pay_per_trip, fuel_per_trip, vehicle_id))
    conn.commit()
    conn.close()

def delete_vehicle(vehicle_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vehicles WHERE id = ?", (vehicle_id,))
    conn.commit()
    conn.close()

def get_driver_trip_summary():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT v.plate_number, v.driver_name, v.pay_per_trip, v.fuel_per_trip, COALESCE(SUM(oi.trips_count), 0) as total_trips, COALESCE(SUM(oi.total_volume), 0) as total_volume_delivered FROM vehicles v LEFT JOIN orders o ON v.id = o.vehicle_id LEFT JOIN order_items oi ON o.id = oi.order_id GROUP BY v.id ORDER BY total_trips DESC""")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
