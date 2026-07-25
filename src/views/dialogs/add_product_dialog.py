import tkinter as tk
from tkinter import ttk, messagebox
from dao import product_dao

class AddProductDialog(tk.Toplevel):
    def __init__(self, parent, on_success_callback=None):
        super().__init__(parent)
        self.on_success_callback = on_success_callback
        
        self.title("Thêm Vật Liệu Mới")
        self.geometry("600x380")
        self.grab_set()

        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self, text="Thêm Loại Vật Liệu Mới", font=("Segoe UI", 12, "bold")).pack(pady=10)

        form = ttk.Frame(self, padding=10)
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

        self.entries = {}
        for i, (label_text, var_name) in enumerate(fields):
            ttk.Label(form, text=label_text).grid(row=i, column=0, sticky="w", pady=3)
            
            if var_name == "ent_unit":
                ent = ttk.Combobox(form, width=23, values=["m³", "chuyến", "bao", "viên", "kg", "tấn"])
                ent.current(0)
            else:
                ent = ttk.Entry(form, width=25)
                
            ent.grid(row=i, column=1, pady=3, sticky="ew")
            self.entries[var_name] = ent
            
            if var_name == "ent_price":
                self.lbl_price_text = tk.Label(form, text="", font=("Segoe UI", 9, "italic"), fg="#059669")
                self.lbl_price_text.grid(row=i, column=2, sticky="w", padx=10)
                def on_price_change(e):
                    from utils import num2vietnamese_words
                    val = self.entries["ent_price"].get().replace(",", "")
                    self.lbl_price_text.config(text=num2vietnamese_words(val))
                ent.bind("<KeyRelease>", on_price_change)

        self.entries["ent_min"].insert(0, "20")

        tk.Button(self, text="Lưu Vật Liệu", bg="#2563eb", fg="white", font=("Segoe UI", 10, "bold"), command=self.save).pack(pady=10)

    def save(self):
        try:
            product_dao.add_product(
                self.entries["ent_code"].get().upper(),
                self.entries["ent_name"].get(),
                self.entries["ent_unit"].get(),
                float(self.entries["ent_price"].get() or 0),
                float(self.entries["ent_stock"].get() or 0),
                float(self.entries["ent_min"].get() or 10),
                self.entries["ent_note"].get()
            )
            messagebox.showinfo("Thành công", "Đã thêm vật liệu mới!")
            self.destroy()
            if self.on_success_callback:
                self.on_success_callback()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm sản phẩm: {str(e)}")
