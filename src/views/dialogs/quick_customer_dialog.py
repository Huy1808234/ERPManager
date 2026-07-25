import tkinter as tk
from tkinter import ttk, messagebox
import config
from dao import customer_dao
from utils import num2vietnamese_words

def open_quick_customer_dialog(parent):
    dlg = tk.Toplevel(parent)
    dlg.title("Thêm Khách Hàng Nhanh")
    dlg.geometry("380x300")
    dlg.grab_set()

    ttk.Label(dlg, text="TẠO NHANH HỒ SƠ KHÁCH HÀNG", font=("Segoe UI", 11, "bold"), foreground=config.COLOR_PRIMARY).pack(pady=10)

    form = ttk.Frame(dlg, padding=10)
    form.pack(fill="both", expand=True)

    ttk.Label(form, text="Họ tên Khách / Nhà thầu:").grid(row=0, column=0, sticky="w", pady=3)
    ent_name = ttk.Entry(form, width=24)
    ent_name.grid(row=0, column=1, pady=3)
    if parent.ent_search.get():
        ent_name.insert(0, parent.ent_search.get().strip())

    ttk.Label(form, text="Số điện thoại:").grid(row=1, column=0, sticky="w", pady=3)
    ent_phone = ttk.Entry(form, width=24)
    ent_phone.grid(row=1, column=1, pady=3)

    ttk.Label(form, text="Địa chỉ công trình:").grid(row=2, column=0, sticky="w", pady=3)
    ent_addr = ttk.Entry(form, width=24)
    ent_addr.grid(row=2, column=1, pady=3)

    ttk.Label(form, text="Hạn mức cho nợ (đ):").grid(row=3, column=0, sticky="w", pady=3)
    ent_limit = ttk.Entry(form, width=24)
    ent_limit.insert(0, str(int(config.DEFAULT_CREDIT_LIMIT)))
    ent_limit.grid(row=3, column=1, pady=3)

    ttk.Label(form, text="Bằng chữ:").grid(row=4, column=0, sticky="w", pady=3)
    lbl_limit_words = ttk.Label(form, text="Năm mươi triệu đồng", font=("Segoe UI", 9, "italic", "bold"), foreground=config.COLOR_PRIMARY)
    lbl_limit_words.grid(row=4, column=1, sticky="w", pady=3)

    def on_limit_change(event=None):
        val = ent_limit.get().strip()
        words = num2vietnamese_words(val)
        lbl_limit_words.config(text=words)

    ent_limit.bind("<KeyRelease>", on_limit_change)

    def save_quick_customer():
        name = ent_name.get().strip()
        if not name:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên khách hàng!")
            return
        try:
            customer_dao.add_customer(name, ent_phone.get().strip(), ent_addr.get().strip(), float(ent_limit.get() or config.DEFAULT_CREDIT_LIMIT), 1)
            messagebox.showinfo("Thành công", f"Đã tạo khách hàng: {name}")
            dlg.destroy()
            parent.load_data()
            for i, c in enumerate(parent.customers):
                if c['name'] == name:
                    parent.cbo_customer.current(i)
                    break
            if parent.refresh_callback:
                parent.refresh_callback()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo khách hàng: {str(e)}")

    tk.Button(dlg, text=" LƯU KHÁCH HÀNG", bg=config.COLOR_PRIMARY, fg="white", font=("Segoe UI", 10, "bold"), pady=4, command=save_quick_customer).pack(pady=10)
