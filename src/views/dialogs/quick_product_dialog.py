import tkinter as tk
from tkinter import ttk, messagebox
import config
from dao import product_dao

def open_quick_product_dialog(parent):
    dlg = tk.Toplevel(parent)
    dlg.title("Thêm Vật Liệu Nhanh")
    dlg.geometry("380x320")
    dlg.grab_set()

    ttk.Label(dlg, text="TẠO NHANH VẬT LIỆU MỚI", font=("Segoe UI", 11, "bold"), foreground=config.COLOR_SUCCESS_DARK).pack(pady=10)

    form = ttk.Frame(dlg, padding=10)
    form.pack(fill="both", expand=True)

    fields = [
        ("Mã SP (vd: CAT_MO):", "ent_code"),
        ("Tên vật liệu:", "ent_name"),
        ("Đơn vị tính (m³, bao, viên):", "ent_unit"),
        ("Đơn giá bán (đ):", "ent_price"),
        ("Số lượng tồn ban đầu:", "ent_stock"),
    ]

    entries = {}
    for i, (label_text, var_name) in enumerate(fields):
        ttk.Label(form, text=label_text).grid(row=i, column=0, sticky="w", pady=3)
        ent = ttk.Entry(form, width=22)
        ent.grid(row=i, column=1, pady=3, sticky="ew")
        entries[var_name] = ent

    entries["ent_unit"].insert(0, "m³")

    def save_quick_product():
        name = entries["ent_name"].get().strip()
        code = entries["ent_code"].get().strip().upper() or f"VL_{name[:3].upper()}"
        if not name:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên vật liệu!")
            return
        try:
            product_dao.add_product(
                code, name, entries["ent_unit"].get(),
                float(entries["ent_price"].get() or 0),
                float(entries["ent_stock"].get() or 100),
                config.DEFAULT_MIN_STOCK, "Tạo nhanh từ màn hình bán hàng"
            )
            messagebox.showinfo("Thành công", f"Đã tạo vật liệu mới: {name}")
            dlg.destroy()
            parent.load_data()
            for i, p in enumerate(parent.products):
                if p['name'] == name:
                    parent.cbo_product.current(i)
                    parent.on_product_change(None)
                    break
            if parent.refresh_callback:
                parent.refresh_callback()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo vật liệu: {str(e)}")

    tk.Button(dlg, text=" LƯU VẬT LIỆU", bg=config.COLOR_SUCCESS_DARK, fg="white", font=("Segoe UI", 10, "bold"), pady=4, command=save_quick_product).pack(pady=10)
