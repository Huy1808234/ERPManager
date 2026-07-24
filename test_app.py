r"""
Automated Test Suite for VLXD Thống Nhất (Tân Phước)
Run tests command:
& "$env:LocalAppData\Programs\Python\Python312\python.exe" test_app.py
"""

import unittest
import database

class TestVLXDSystem(unittest.TestCase):
    def setUp(self):
        database.init_db()

    def test_database_tables_seeded(self):
        """Test products, customers, and vehicles are properly pre-populated"""
        products = database.get_all_products()
        customers = database.get_all_customers()
        vehicles = database.get_all_vehicles()

        self.assertGreater(len(products), 0, "Danh mục sản phẩm không được rỗng")
        self.assertGreater(len(customers), 0, "Danh mục khách hàng không được rỗng")
        self.assertGreater(len(vehicles), 0, "Danh mục đội xe không được rỗng")

    def test_volume_and_price_calculation(self):
        """Test formula: 2.2 m³ x 8 trips = 17.6 m³"""
        vol_per_trip = 2.2
        trips = 8
        unit_price = 280000  # Đá 0x4
        shipping_cost = 150000
        paid_amount = 0

        # Run transaction
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

if __name__ == "__main__":
    unittest.main()
