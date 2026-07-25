import tkinter as tk
from tkinter import ttk, messagebox
from dao import customer_dao

class CustomerTable(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        columns = ("id", "name", "phone", "address", "is_contractor", "debt", "limit", "created_at")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=16)

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Họ Tên Khách Hàng / Nhà Thầu")
        self.tree.heading("phone", text="Số Điện Thoại")
        self.tree.heading("address", text="Địa Chỉ / Công Trình Chi Tiết")
        self.tree.heading("is_contractor", text="Phân Loại")
        self.tree.heading("debt", text="Nợ Hiện Tại")
        self.tree.heading("limit", text="Hạn Mức Cho Nợ")
        self.tree.heading("created_at", text="Ngày Tạo")

        self.tree.column("id", width=40)
        self.tree.column("name", width=220)
        self.tree.column("phone", width=110)
        self.tree.column("address", width=250)
        self.tree.column("is_contractor", width=110)
        self.tree.column("debt", width=120, anchor="e")
        self.tree.column("limit", width=120, anchor="e")
        self.tree.column("created_at", width=140)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_customers(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        customers = customer_dao.get_all_customers()
        for c in customers:
            type_str = "🏗️ Nhà thầu/Sỉ" if c['is_contractor'] else "🏠 Khách lẻ"
            self.tree.insert("", "end", values=(
                c['id'],
                c['name'],
                c['phone'] or "",
                c['address'] or "",
                type_str,
                f"{c['debt']:,.0f}đ",
                f"{c['credit_limit']:,.0f}đ",
                c['created_at'] or ""
            ))
            
    def get_selected_customer_id(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return None
        values = self.tree.item(selected_item[0])['values']
        return values[0]
