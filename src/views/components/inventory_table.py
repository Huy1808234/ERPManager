import tkinter as tk
from tkinter import ttk
from dao import product_dao

class InventoryTable(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        columns = ("id", "code", "name", "unit", "price", "stock", "min_stock", "status", "note")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=16)

        self.tree.heading("id", text="ID")
        self.tree.heading("code", text="Mã SP")
        self.tree.heading("name", text="Tên Vật Liệu")
        self.tree.heading("unit", text="ĐVT")
        self.tree.heading("price", text="Đơn Giá Chuẩn")
        self.tree.heading("stock", text="Tồn Kho Hiện Tại")
        self.tree.heading("min_stock", text="Ngưỡng Báo Dưới")
        self.tree.heading("status", text="Trạng Thái Kho")
        self.tree.heading("note", text="Ghi Chú")

        self.tree.column("id", width=40)
        self.tree.column("code", width=100)
        self.tree.column("name", width=220)
        self.tree.column("unit", width=60)
        self.tree.column("price", width=110)
        self.tree.column("stock", width=130)
        self.tree.column("min_stock", width=120)
        self.tree.column("status", width=130)
        self.tree.column("note", width=200)

        # Style tags for rows
        self.tree.tag_configure("low_stock", background="#fecaca", foreground="#b91c1c")
        self.tree.tag_configure("normal", background="#ffffff")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_inventory(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        products = product_dao.get_all_products()
        for p in products:
            status = "🔴 SẮP HẾT HÀNG" if p['stock'] <= p['min_stock'] else "🟢 ĐỦ HÀNG"
            tag = "low_stock" if p['stock'] <= p['min_stock'] else "normal"

            self.tree.insert("", "end", values=(
                p['id'],
                p['code'],
                p['name'],
                p['unit'],
                f"{p['price']:,.0f}đ",
                f"{p['stock']:,.1f} {p['unit']}",
                f"{p['min_stock']:,.1f} {p['unit']}",
                status,
                p['note'] or ""
            ), tags=(tag,))
            
    def get_selected_product(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return None
        values = self.tree.item(selected_item[0])['values']
        return values
