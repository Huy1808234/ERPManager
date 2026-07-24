"""
Inventory & Stock Management View for VLXD Thống Nhất
Tracks imports from quarries, stock levels, and full CRUD (Thêm, Sửa, Xóa).
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database

class InventoryView(ttk.Frame):
    def __init__(self, parent, refresh_callback=None):
        super().__init__(parent, padding=10)
        self.refresh_callback = refresh_callback
        self.setup_ui()
        self.load_inventory()

    def setup_ui(self):
        title_frame = ttk.Frame(self)
        title_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(title_frame, text="📦 QUẢN LÝ KHO HÀNG & TỒN KHO VẬT TƯ", font=("Segoe UI", 14, "bold"), foreground="#1e3a8a").pack(side="left")

        # Top Control Bar (Add, Edit, Delete, Stock Import)
        btn_bar = ttk.Frame(self)
        btn_bar.pack(fill="x", pady=(0, 10))

        tk.Button(btn_bar, text="➕ Thêm Vật Liệu", bg="#2563eb", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5, command=self.open_add_product_dialog).pack(side="left", padx=(0, 5))
        tk.Button(btn_bar, text="✏️ Sửa Vật Liệu", bg="#d97706", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5, command=self.open_edit_product_dialog).pack(side="left", padx=(0, 5))
        tk.Button(btn_bar, text="❌ Xóa Vật Liệu", bg="#dc2626", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5, command=self.delete_selected_product).pack(side="left", padx=(0, 5))
        tk.Button(btn_bar, text="🚚 Nhập Hàng Từ Mỏ (Tăng Kho)", bg="#059669", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5, command=self.open_import_stock_dialog).pack(side="left", padx=(0, 5))
        tk.Button(btn_bar, text="🔄 Tải Lại Kho", bg="#64748b", fg="white", font=("Segoe UI", 10), padx=10, pady=5, command=self.load_inventory).pack(side="right")

        # Inventory Table
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

        products = database.get_all_products()
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

    def open_add_product_dialog(self):
        dlg = tk.Toplevel(self)
        dlg.title("Thêm Vật Liệu Mới")
        dlg.geometry("400x380")
        dlg.grab_set()

        ttk.Label(dlg, text="Thêm Loại Vật Liệu Mới", font=("Segoe UI", 12, "bold")).pack(pady=10)

        form = ttk.Frame(dlg, padding=10)
        form.pack(fill="both", expand=True)

        fields = [
            ("Mã sản phẩm:", "ent_code"),
            ("Tên vật liệu:", "ent_name"),
            ("Đơn vị tính (m³, bao, viên):", "ent_unit"),
            ("Đơn giá bán (đ):", "ent_price"),
            ("Số lượng tồn ban đầu:", "ent_stock"),
            ("Ngưỡng cảnh báo hết:", "ent_min"),
            ("Ghi chú:", "ent_note"),
        ]

        entries = {}
        for i, (label_text, var_name) in enumerate(fields):
            ttk.Label(form, text=label_text).grid(row=i, column=0, sticky="w", pady=3)
            ent = ttk.Entry(form, width=25)
            ent.grid(row=i, column=1, pady=3, sticky="ew")
            entries[var_name] = ent

        entries["ent_unit"].insert(0, "m³")
        entries["ent_min"].insert(0, "20")

        def save():
            try:
                database.add_product(
                    entries["ent_code"].get().upper(),
                    entries["ent_name"].get(),
                    entries["ent_unit"].get(),
                    float(entries["ent_price"].get() or 0),
                    float(entries["ent_stock"].get() or 0),
                    float(entries["ent_min"].get() or 10),
                    entries["ent_note"].get()
                )
                messagebox.showinfo("Thành công", "Đã thêm vật liệu mới!")
                dlg.destroy()
                self.load_inventory()
                if self.refresh_callback:
                    self.refresh_callback()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể thêm sản phẩm: {str(e)}")

        tk.Button(dlg, text="Lưu Vật Liệu", bg="#2563eb", fg="white", font=("Segoe UI", 10, "bold"), command=save).pack(pady=10)

    def open_edit_product_dialog(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn vật liệu cần sửa từ danh sách!")
            return

        values = self.tree.item(selected_item[0])['values']
        prod_id = values[0]
        
        products = database.get_all_products()
        prod = [p for p in products if p['id'] == prod_id]
        if not prod:
            return
        p = prod[0]

        dlg = tk.Toplevel(self)
        dlg.title("Sửa Thông Tin Vật Liệu")
        dlg.geometry("400x380")
        dlg.grab_set()

        ttk.Label(dlg, text="Cập Nhật Thông Tin Vật Liệu", font=("Segoe UI", 12, "bold"), foreground="#d97706").pack(pady=10)

        form = ttk.Frame(dlg, padding=10)
        form.pack(fill="both", expand=True)

        fields = [
            ("Mã sản phẩm:", "ent_code", p['code']),
            ("Tên vật liệu:", "ent_name", p['name']),
            ("Đơn vị tính:", "ent_unit", p['unit']),
            ("Đơn giá bán (đ):", "ent_price", str(int(p['price']))),
            ("Số lượng tồn kho:", "ent_stock", str(p['stock'])),
            ("Ngưỡng cảnh báo hết:", "ent_min", str(p['min_stock'])),
            ("Ghi chú:", "ent_note", p['note'] or ""),
        ]

        entries = {}
        for i, (label_text, var_name, default_val) in enumerate(fields):
            ttk.Label(form, text=label_text).grid(row=i, column=0, sticky="w", pady=3)
            ent = ttk.Entry(form, width=25)
            ent.insert(0, default_val)
            ent.grid(row=i, column=1, pady=3, sticky="ew")
            entries[var_name] = ent

        def update():
            try:
                database.update_product(
                    prod_id,
                    entries["ent_code"].get().upper(),
                    entries["ent_name"].get(),
                    entries["ent_unit"].get(),
                    float(entries["ent_price"].get() or 0),
                    float(entries["ent_stock"].get() or 0),
                    float(entries["ent_min"].get() or 10),
                    entries["ent_note"].get()
                )
                messagebox.showinfo("Thành công", f"Đã cập nhật vật liệu {entries['ent_name'].get()}!")
                dlg.destroy()
                self.load_inventory()
                if self.refresh_callback:
                    self.refresh_callback()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể cập nhật sản phẩm: {str(e)}")

        tk.Button(dlg, text="💾 Cập Nhật Vật Liệu", bg="#d97706", fg="white", font=("Segoe UI", 10, "bold"), command=update).pack(pady=10)

    def delete_selected_product(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn vật liệu cần xóa!")
            return

        values = self.tree.item(selected_item[0])['values']
        prod_id = values[0]
        prod_name = values[2]

        if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc chắn muốn XÓA vật liệu [{prod_name}] khỏi hệ thống kho?"):
            try:
                database.delete_product(prod_id)
                messagebox.showinfo("Thành công", f"Đã xóa thành công vật liệu [{prod_name}]!")
                self.load_inventory()
                if self.refresh_callback:
                    self.refresh_callback()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa vật liệu: {str(e)}")

    def open_import_stock_dialog(self):
        products = database.get_all_products()
        if not products:
            return

        dlg = tk.Toplevel(self)
        dlg.title("Nhập Hàng Từ Mỏ")
        dlg.geometry("380x250")
        dlg.grab_set()

        ttk.Label(dlg, text="Nhập Hàng Tăng Kho Bãi", font=("Segoe UI", 12, "bold")).pack(pady=10)

        form = ttk.Frame(dlg, padding=10)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text="Chọn vật liệu nhập:").grid(row=0, column=0, sticky="w", pady=5)
        cbo_prod = ttk.Combobox(form, width=25, state="readonly", values=[p['name'] for p in products])
        cbo_prod.grid(row=0, column=1, pady=5)
        cbo_prod.current(0)

        ttk.Label(form, text="Số lượng nhập vào:").grid(row=1, column=0, sticky="w", pady=5)
        ent_qty = ttk.Entry(form, width=25)
        ent_qty.grid(row=1, column=1, pady=5)

        ttk.Label(form, text="Ghi chú (Mỏ/Chuyến nhập):").grid(row=2, column=0, sticky="w", pady=5)
        ent_note = ttk.Entry(form, width=25)
        ent_note.insert(0, "Nhập mỏ cát/đá")
        ent_note.grid(row=2, column=1, pady=5)

        def save_import():
            try:
                idx = cbo_prod.current()
                prod_id = products[idx]['id']
                qty = float(ent_qty.get())
                note = ent_note.get()

                database.update_inventory_stock(prod_id, qty, note)
                messagebox.showinfo("Thành công", f"Đã cộng {qty} vào kho {products[idx]['name']}!")
                dlg.destroy()
                self.load_inventory()
                if self.refresh_callback:
                    self.refresh_callback()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể nhập kho: {str(e)}")

        tk.Button(dlg, text="Xác Nhận Nhập Kho", bg="#059669", fg="white", font=("Segoe UI", 10, "bold"), command=save_import).pack(pady=10)
