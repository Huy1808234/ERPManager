"""
Sales & Volume Calculation View for VLXD Thống Nhất
Refactored into Component-based UI.
"""

import tkinter as tk
from tkinter import ttk
import config

from views.components.sales_form import SalesForm
from views.components.sales_table import SalesHistoryTable

class SalesView(ttk.Frame):
    def __init__(self, parent, refresh_callback=None):
        super().__init__(parent, padding=10)
        self.refresh_callback = refresh_callback
        self.setup_ui()

    def setup_ui(self):
        # 1. Title Banner
        title_frame = ttk.Frame(self)
        title_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(title_frame, text=" TẠO ĐƠN HÀNG & TÍNH KHỐI LƯỢNG VẬT LIỆU", font=("Segoe UI", 14, "bold"), foreground=config.COLOR_PRIMARY_DARK).pack(side="left")
        ttk.Label(title_frame, text="*Công thức: Số khối x Số chuyến = Tổng m³*", font=("Segoe UI", 10, "italic"), foreground=config.COLOR_SECONDARY_DARK).pack(side="right")

        # 2. Main Layout
        content_box = ttk.Frame(self)
        content_box.pack(fill="both", expand=True)

        # RIGHT: History Table (Initialize first so Form can reference its reload method)
        self.sales_table = SalesHistoryTable(content_box)
        self.sales_table.pack(side="right", fill="both", expand=True)

        def on_order_created():
            # When an order is created by the form, reload the table and trigger global refresh
            self.sales_table.load_orders_table()
            if self.refresh_callback:
                self.refresh_callback()

        # LEFT: Entry Form
        self.sales_form = SalesForm(content_box, on_order_created=on_order_created)
        self.sales_form.pack(side="left", fill="both", expand=False, padx=(0, 10))

    def load_data(self):
        """Called by main.py during a cross-tab refresh"""
        self.sales_form.load_data()
        self.sales_table.load_orders_table()
