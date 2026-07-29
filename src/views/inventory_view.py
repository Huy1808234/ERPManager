"""
Inventory & Stock Management View for VLXD Thống Nhất
Refactored into Component-based UI.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from dao import product_dao

from views.components.inventory_table import InventoryTable
from views.dialogs.add_product_dialog import AddProductDialog
from views.dialogs.edit_product_dialog import EditProductDialog
from views.dialogs.import_stock_dialog import ImportStockDialog

class InventoryView(ttk.Frame):
    def __init__(self, parent, refresh_callback=None):
        super().__init__(parent, padding=10)
        self.refresh_callback = refresh_callback
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        title_frame = ttk.Frame(self)
        title_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(title_frame, text=" QUẢN LÝ KHO HÀNG & TỒN KHO VẬT TƯ", font=("Segoe UI", 14, "bold"), foreground="#1e3a8a").pack(side="left")

        # Top Control Bar (Add, Edit, Delete, Stock Import)
        btn_bar = ttk.Frame(self)
        btn_bar.pack(fill="x", pady=(0, 10))

        tk.Button(btn_bar, text=" Thêm Vật Liệu", bg="#2563eb", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5, command=self.open_add_product_dialog).pack(side="left", padx=(0, 5))
        tk.Button(btn_bar, text=" Sửa Vật Liệu", bg="#d97706", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5, command=self.open_edit_product_dialog).pack(side="left", padx=(0, 5))
        tk.Button(btn_bar, text=" Xóa Vật Liệu", bg="#dc2626", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5, command=self.delete_selected_product).pack(side="left", padx=(0, 5))
        tk.Button(btn_bar, text=" Nhập Hàng Từ Mỏ (Tăng Kho)", bg="#059669", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5, command=self.open_import_stock_dialog).pack(side="left", padx=(0, 5))
        tk.Button(btn_bar, text=" Tải Lại Kho", bg="#64748b", fg="white", font=("Segoe UI", 10), padx=10, pady=5, command=self.load_data).pack(side="right")

        # Inventory Table Component
        self.inventory_table = InventoryTable(self)
        self.inventory_table.pack(fill="both", expand=True)

    def load_data(self):
        self.inventory_table.load_inventory()

    def on_dialog_success(self):
        self.load_data()
        if self.refresh_callback:
            self.refresh_callback()

    def open_add_product_dialog(self):
        AddProductDialog(self, on_success_callback=self.on_dialog_success)

    def open_edit_product_dialog(self):
        prod = self.inventory_table.get_selected_product()
        if not prod:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn vật liệu cần sửa từ danh sách!")
            return

        prod_id = prod[0]
        products = product_dao.get_all_products()
        p_list = [p for p in products if p['id'] == prod_id]
        if not p_list:
            return
            
        EditProductDialog(self, product=p_list[0], on_success_callback=self.on_dialog_success)

    def delete_selected_product(self):
        prod = self.inventory_table.get_selected_product()
        if not prod:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn vật liệu cần xóa!")
            return

        prod_id = prod[0]
        prod_name = prod[2]

        if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc chắn muốn XÓA vật liệu [{prod_name}] khỏi hệ thống kho?"):
            try:
                product_dao.delete_product(prod_id)
                messagebox.showinfo("Thành công", f"Đã xóa thành công vật liệu [{prod_name}]!")
                self.on_dialog_success()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa vật liệu: {str(e)}")

    def open_import_stock_dialog(self):
        ImportStockDialog(self, on_success_callback=self.on_dialog_success)
