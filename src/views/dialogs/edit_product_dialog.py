import tkinter as tk
from tkinter import ttk, messagebox
from dao import product_dao

class EditProductDialog(tk.Toplevel):
    def __init__(self, parent, product, on_success_callback=None):
        super().__init__(parent)
        self.on_success_callback = on_success_callback
        self.product = product
        
        self.title("Sửa Thông Tin Vật Liệu")
        self.geometry("600x380")
        self.grab_set()

        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self, text="Cập Nhật Thông Tin Vật Liệu", font=("Segoe UI", 12, "bold"), foreground="#d97706").pack(pady=10)

        form = ttk.Frame(self, padding=10)
        form.pack(fill="both", expand=True)

        p = self.product
        fields = [
            ("Mã sản phẩm:", "ent_code", p['code']),
            ("Tên vật liệu:", "ent_name", p['name']),
            ("Đơn vị tính:", "ent_unit", p['unit']),
            ("Đơn giá bán (đ):", "ent_price", str(int(p['price']))),
            ("Số lượng tồn kho:", "ent_stock", str(p['stock'])),
            ("Ngưỡng cảnh báo hết:", "ent_min", str(p['min_stock'])),
            ("Ghi chú:", "ent_note", p['note'] or ""),
        ]

        self.entries = {}
        for i, (label_text, var_name, default_val) in enumerate(fields):
            ttk.Label(form, text=label_text).grid(row=i, column=0, sticky="w", pady=3)
            ent = ttk.Entry(form, width=25)
            ent.insert(0, default_val)
            ent.grid(row=i, column=1, pady=3, sticky="ew")
            self.entries[var_name] = ent
            
            if var_name == "ent_price":
                self.lbl_price_text = tk.Label(form, text="", font=("Segoe UI", 9, "italic"), fg="#059669")
                self.lbl_price_text.grid(row=i, column=2, sticky="w", padx=10)
                def on_price_change(e=None):
                    from utils import num2vietnamese_words
                    val = self.entries["ent_price"].get().replace(",", "")
                    self.lbl_price_text.config(text=num2vietnamese_words(val))
                ent.bind("<KeyRelease>", on_price_change)
                on_price_change() # Init text

        tk.Button(self, text="💾 Cập Nhật Vật Liệu", bg="#d97706", fg="white", font=("Segoe UI", 10, "bold"), command=self.update).pack(pady=10)

    def update(self):
        try:
            product_dao.update_product(
                self.product['id'],
                self.entries["ent_code"].get().upper(),
                self.entries["ent_name"].get(),
                self.entries["ent_unit"].get(),
                float(self.entries["ent_price"].get() or 0),
                float(self.entries["ent_stock"].get() or 0),
                float(self.entries["ent_min"].get() or 10),
                self.entries["ent_note"].get()
            )
            messagebox.showinfo("Thành công", f"Đã cập nhật vật liệu {self.entries['ent_name'].get()}!")
            self.destroy()
            if self.on_success_callback:
                self.on_success_callback()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật sản phẩm: {str(e)}")
