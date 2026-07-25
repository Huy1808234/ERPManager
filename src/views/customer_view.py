"""
Customer & Contractor Management View for VLXD Thống Nhất
Refactored into Component-based UI.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from dao import customer_dao

from views.components.customer_table import CustomerTable
from views.dialogs.add_customer_dialog import AddCustomerDialog
from views.dialogs.edit_customer_dialog import EditCustomerDialog

class CustomerView(ttk.Frame):
    def __init__(self, parent, refresh_callback=None):
        super().__init__(parent, padding=10)
        self.refresh_callback = refresh_callback
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        title_frame = ttk.Frame(self)
        title_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(title_frame, text="👥 QUẢN LÝ HỒ SƠ KHÁCH HÀNG & NHÀ THẦU", font=("Segoe UI", 14, "bold"), foreground="#1e3a8a").pack(side="left")

        # Top Control Bar (Add, Edit, Delete)
        btn_bar = ttk.Frame(self)
        btn_bar.pack(fill="x", pady=(0, 10))

        tk.Button(btn_bar, text="➕ Thêm Khách Hàng", bg="#2563eb", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5, command=self.open_add_customer_dialog).pack(side="left", padx=(0, 5))
        tk.Button(btn_bar, text="✏️ Sửa Khách Hàng", bg="#d97706", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5, command=self.open_edit_customer_dialog).pack(side="left", padx=(0, 5))
        tk.Button(btn_bar, text="❌ Xóa Khách Hàng", bg="#dc2626", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5, command=self.delete_selected_customer).pack(side="left", padx=(0, 5))
        tk.Button(btn_bar, text="🔄 Tải Lại Danh Sách", bg="#64748b", fg="white", font=("Segoe UI", 10), padx=10, pady=5, command=self.load_data).pack(side="right")

        # Customers Table Component
        self.customer_table = CustomerTable(self)
        self.customer_table.pack(fill="both", expand=True)

    def load_data(self):
        self.customer_table.load_customers()

    def on_dialog_success(self):
        self.load_data()
        if self.refresh_callback:
            self.refresh_callback()

    def open_add_customer_dialog(self):
        AddCustomerDialog(self, on_success_callback=self.on_dialog_success)

    def open_edit_customer_dialog(self):
        cust_id = self.customer_table.get_selected_customer_id()
        if not cust_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn khách hàng cần sửa từ danh sách!")
            return

        customers = customer_dao.get_all_customers()
        c_list = [c for c in customers if c['id'] == cust_id]
        if not c_list:
            return
            
        EditCustomerDialog(self, customer=c_list[0], on_success_callback=self.on_dialog_success)

    def delete_selected_customer(self):
        cust_id = self.customer_table.get_selected_customer_id()
        if not cust_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn khách hàng cần xóa từ danh sách!")
            return
            
        # Get customer name for confirmation message
        customers = customer_dao.get_all_customers()
        c_list = [c for c in customers if c['id'] == cust_id]
        if not c_list:
            return
        cust_name = c_list[0]['name']

        if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa khách hàng [{cust_name}]?\nHành động này không thể hoàn tác."):
            try:
                customer_dao.delete_customer(cust_id)
                messagebox.showinfo("Thành công", f"Đã xóa thành công khách hàng [{cust_name}]!")
                self.on_dialog_success()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa khách hàng: {str(e)}")
