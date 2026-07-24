"""
MAIN ENTRY POINT - VẬT LIỆU XÂY DỰNG THỐNG NHẤT (TÂN PHƯỚC)
Desktop Application using Python + SQLite + MVC Architecture.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

import database
from views.sales_view import SalesView
from views.inventory_view import InventoryView
from views.dispatch_view import DispatchView
from views.debt_view import DebtView
from views.customer_view import CustomerView
from views.payroll_view import PayrollView

class VLXDApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("VẬT LIỆU XÂY DỰNG THỐNG NHẤT - BÃI CÁT ĐÁ TÂN PHƯỚC (QUẢN LÝ NỘI BỘ)")
        self.geometry("1240x730")
        self.minsize(1024, 600)

        # Apply clean ttk theme styling
        style = ttk.Style(self)
        style.theme_use("clam")

        # Custom Colors & Fonts
        style.configure(".", font=("Segoe UI", 10))
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[12, 8])
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#e2e8f0", foreground="#0f172a")

        # Initialize SQLite DB
        database.init_db()

        self.setup_ui()

    def setup_ui(self):
        # 1. Header Banner
        header = ttk.Frame(self)
        header.pack(fill="x", ipady=6)

        lbl_company = tk.Label(
            header,
            text="🏗️ VẬT LIỆU XÂY DỰNG THỐNG NHẤT - BÃI CÁT ĐÁ TÂN PHƯỚC",
            font=("Segoe UI", 16, "bold"),
            fg="#1e3a8a"
        )
        lbl_company.pack(side="left", padx=10)

        lbl_subtitle = tk.Label(
            header,
            text="📍 Tân Phước, TX. Phú Mỹ | 📞 Hotline: 0908.123.456 | 🟢 Offline LAN $0 VNĐ",
            font=("Segoe UI", 10),
            fg="#475569"
        )
        lbl_subtitle.pack(side="right", padx=10)

        # 2. Main Tabbed Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # Tab 1: Sales
        self.sales_tab = SalesView(self.notebook, refresh_callback=self.refresh_all_tabs)
        self.notebook.add(self.sales_tab, text="🛒 Bán Hàng & Tính Số Khối")

        # Tab 2: Inventory
        self.inventory_tab = InventoryView(self.notebook, refresh_callback=self.refresh_all_tabs)
        self.notebook.add(self.inventory_tab, text="📦 Quản Lý Kho & Vật Tư")

        # Tab 3: Dispatch & Drivers
        self.dispatch_tab = DispatchView(self.notebook, refresh_callback=self.refresh_all_tabs)
        self.notebook.add(self.dispatch_tab, text="🚚 Điều Xe & Số Chuyến")

        # Tab 4: Debt & Cash Flow
        self.debt_tab = DebtView(self.notebook, refresh_callback=self.refresh_all_tabs)
        self.notebook.add(self.debt_tab, text="💳 Công Nợ Nhà Thầu")

        # Tab 5: Customers
        self.customer_tab = CustomerView(self.notebook, refresh_callback=self.refresh_all_tabs)
        self.notebook.add(self.customer_tab, text="👥 Hồ Sơ Khách Hàng")

        # Tab 6: Payroll & Salary Management
        self.payroll_tab = PayrollView(self.notebook, refresh_callback=self.refresh_all_tabs)
        self.notebook.add(self.payroll_tab, text="💵 Quản Lý Bảng Lương")

        # 3. Status Footer Bar
        footer = ttk.Frame(self)
        footer.pack(fill="x", side="bottom", ipady=3)

        lbl_status = tk.Label(
            footer,
            text="✅ Dữ liệu SQLite lưu cục bộ: vlxd_thongnhat.db | Giờ hoạt động: 06:00 - 18:00 (T2-T7), 06:00 - 17:00 (CN)",
            font=("Segoe UI", 9),
            fg="#475569",
            bg="#f1f5f9"
        )
        lbl_status.pack(side="left", padx=10)

        lbl_version = tk.Label(
            footer,
            text="Kiến trúc MVC v1.0 (Bãi VLXD Thống Nhất)",
            font=("Segoe UI", 9, "italic"),
            fg="#64748b",
            bg="#f1f5f9"
        )
        lbl_version.pack(side="right", padx=10)

    def refresh_all_tabs(self):
        """Cross-tab refresh controller"""
        self.sales_tab.load_data()
        self.inventory_tab.load_inventory()
        self.dispatch_tab.load_dispatch_data()
        self.debt_tab.load_debt_data()
        self.customer_tab.load_customers()
        self.payroll_tab.load_payroll_data()

if __name__ == "__main__":
    app = VLXDApp()
    app.mainloop()
