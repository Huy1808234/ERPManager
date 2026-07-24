r"""
Automated Test Suite for VLXD Thống Nhất (Tân Phước)
"""

import unittest
import database

class TestVLXDSystem(unittest.TestCase):
    def setUp(self):
        database.init_db()
        # Seed test-specific items
        products = database.get_all_products()
        if not products:
            database.add_product("DA_0X4", "Đá 0x4 (Đá cấp phối)", "m³", 280000, 250.0, 30.0, "Test")
        customers = database.get_all_customers()
        if not customers:
            database.add_customer("Nhà thầu Test", "0908123456", "Tân Phước", 50000000, 1)
        vehicles = database.get_all_vehicles()
        if not vehicles:
            database.add_vehicle("60C-123.45", "Tài xế Minh", "0988111222", 2.2, 50000, 30000)
        employees = database.get_all_employees()
        if not employees:
            database.add_employee("NV001", "Tài xế Minh", "0988111222", "Tài xế xe ben", "Theo chuyến", 0, 50000, 500000)

    def test_database_tables_created(self):
        """Test products, customers, vehicles and employees tables exist"""
        products = database.get_all_products()
        customers = database.get_all_customers()
        vehicles = database.get_all_vehicles()
        employees = database.get_all_employees()

        self.assertGreater(len(products), 0, "Danh mục sản phẩm không được rỗng")
        self.assertGreater(len(customers), 0, "Danh mục khách hàng không được rỗng")
        self.assertGreater(len(vehicles), 0, "Danh mục đội xe không được rỗng")
        self.assertGreater(len(employees), 0, "Danh mục nhân viên không được rỗng")

    def test_volume_and_price_calculation(self):
        """Test formula: 2.2 m³ x 8 trips = 17.6 m³"""
        vol_per_trip = 2.2
        trips = 8
        unit_price = 280000  # Đá 0x4
        shipping_cost = 150000
        paid_amount = 0

        customers = database.get_all_customers()
        vehicles = database.get_all_vehicles()
        products = database.get_all_products()

        code, total_vol, total_amt, debt = database.create_order_transaction(
            customers[0]['id'],
            vehicles[0]['id'],
            products[0]['id'],
            vol_per_trip,
            trips,
            unit_price,
            shipping_cost,
            paid_amount,
            "Test Đơn Hàng Đá 0x4"
        )

        expected_volume = 17.6
        expected_product_amt = 17.6 * 280000  # 4,928,000
        expected_total = expected_product_amt + 150000  # 5,078,000

        self.assertAlmostEqual(total_vol, expected_volume, places=2, msg="Tính tổng m³ chưa đúng")
        self.assertAlmostEqual(total_amt, expected_total, places=2, msg="Tính tổng tiền chưa đúng")
        self.assertAlmostEqual(debt, expected_total, places=2, msg="Tính dư nợ chưa đúng")

    def test_debt_payment(self):
        """Test customer debt reduction upon payment"""
        customers = database.get_all_customers()
        cust = customers[0]
        initial_debt = cust['debt']
        pay_amount = 2000000

        database.record_debt_payment(cust['id'], pay_amount, "Thanh toán test")

        updated_customers = database.get_all_customers()
        updated_cust = [c for c in updated_customers if c['id'] == cust['id']][0]

        self.assertAlmostEqual(updated_cust['debt'], initial_debt - pay_amount, places=2, msg="Trừ tiền nợ chưa đúng")

    def test_payroll_calculation(self):
        """Test employee payroll and advance salary calculations"""
        employees = database.get_all_employees()
        emp = employees[0]
        initial_payroll = database.get_payroll_summary()
        initial_adv = [p for p in initial_payroll if p['id'] == emp['id']][0]['advances']

        database.record_salary_advance(emp['id'], 500000, "Tạm ứng test")

        payroll = database.get_payroll_summary()
        emp_pay = [p for p in payroll if p['id'] == emp['id']][0]

        self.assertAlmostEqual(emp_pay['advances'], initial_adv + 500000, places=2, msg="Tính tiền tạm ứng chưa đúng")
        self.assertGreaterEqual(emp_pay['gross_salary'], 500000, "Tổng thu nhập phải >= phụ cấp")

if __name__ == "__main__":
    unittest.main()
