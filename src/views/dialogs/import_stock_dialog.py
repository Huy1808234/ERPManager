import tkinter as tk
from tkinter import ttk, messagebox
from dao import product_dao

class ImportStockDialog(tk.Toplevel):
    def __init__(self, parent, on_success_callback=None):
        super().__init__(parent)
        self.on_success_callback = on_success_callback
        
        self.products = product_dao.get_all_products()
        if not self.products:
            messagebox.showwarning("Cảnh báo", "Không có sản phẩm nào trong kho. Vui lòng thêm sản phẩm trước!")
            self.destroy()
            return
            
        self.title("Nhập Hàng Từ Mỏ")
        self.geometry("380x250")
        self.grab_set()

        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self, text="Nhập Hàng Tăng Kho Bãi", font=("Segoe UI", 12, "bold")).pack(pady=10)

        form = ttk.Frame(self, padding=10)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text="Chọn vật liệu nhập:").grid(row=0, column=0, sticky="w", pady=5)
        self.cbo_prod = ttk.Combobox(form, width=25, state="readonly", values=[p['name'] for p in self.products])
        self.cbo_prod.grid(row=0, column=1, pady=5)
        self.cbo_prod.current(0)

        ttk.Label(form, text="Số lượng nhập vào:").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_qty = ttk.Entry(form, width=25)
        self.ent_qty.grid(row=1, column=1, pady=5)

        ttk.Label(form, text="Ghi chú (Mỏ/Chuyến nhập):").grid(row=2, column=0, sticky="w", pady=5)
        self.ent_note = ttk.Entry(form, width=25)
        self.ent_note.insert(0, "Nhập mỏ cát/đá")
        self.ent_note.grid(row=2, column=1, pady=5)

        tk.Button(self, text="Xác Nhận Nhập Kho", bg="#059669", fg="white", font=("Segoe UI", 10, "bold"), command=self.save_import).pack(pady=10)

    def save_import(self):
        try:
            idx = self.cbo_prod.current()
            prod_id = self.products[idx]['id']
            qty = float(self.ent_qty.get())
            note = self.ent_note.get()

            product_dao.update_inventory_stock(prod_id, qty, note)
            messagebox.showinfo("Thành công", f"Đã cộng {qty} vào kho {self.products[idx]['name']}!")
            self.destroy()
            if self.on_success_callback:
                self.on_success_callback()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể nhập kho: {str(e)}")
