import tkinter as tk
from tkinter import ttk, messagebox
import config
from dao import customer_dao
from utils import num2vietnamese_words

class AddCustomerDialog(tk.Toplevel):
    def __init__(self, parent, on_success_callback=None):
        super().__init__(parent)
        self.on_success_callback = on_success_callback
        
        self.title("Thêm Khách Hàng Mới")
        self.geometry("400x340")
        self.grab_set()

        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self, text="Tạo Hồ Sơ Khách Hàng / Nhà Thầu", font=("Segoe UI", 12, "bold")).pack(pady=10)

        form = ttk.Frame(self, padding=10)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text="Họ tên Khách / Nhà thầu:").grid(row=0, column=0, sticky="w", pady=3)
        self.ent_name = ttk.Entry(form, width=25)
        self.ent_name.grid(row=0, column=1, pady=3)

        ttk.Label(form, text="Số điện thoại:").grid(row=1, column=0, sticky="w", pady=3)
        self.ent_phone = ttk.Entry(form, width=25)
        self.ent_phone.grid(row=1, column=1, pady=3)

        ttk.Label(form, text="Địa chỉ / Công trình:").grid(row=2, column=0, sticky="w", pady=3)
        self.ent_addr = ttk.Entry(form, width=25)
        self.ent_addr.grid(row=2, column=1, pady=3)

        ttk.Label(form, text="Hạn mức cho nợ (đ):").grid(row=3, column=0, sticky="w", pady=3)
        self.ent_limit = ttk.Entry(form, width=25)
        self.ent_limit.insert(0, str(config.DEFAULT_CREDIT_LIMIT))
        self.ent_limit.grid(row=3, column=1, pady=3)

        ttk.Label(form, text="Bằng chữ:").grid(row=4, column=0, sticky="w", pady=3)
        self.lbl_limit_words = ttk.Label(form, text="Năm mươi triệu đồng", font=("Segoe UI", 9, "italic", "bold"), foreground="#2563eb")
        self.lbl_limit_words.grid(row=4, column=1, sticky="w", pady=3)

        self.ent_limit.bind("<KeyRelease>", self.on_limit_change)

        ttk.Label(form, text="Loại khách hàng:").grid(row=5, column=0, sticky="w", pady=3)
        self.var_is_contractor = tk.IntVar(value=1)
        r1 = ttk.Radiobutton(form, text="Nhà thầu / Khách sỉ", variable=self.var_is_contractor, value=1)
        r2 = ttk.Radiobutton(form, text="Khách mua lẻ dân dụng", variable=self.var_is_contractor, value=0)
        r1.grid(row=5, column=1, sticky="w")
        r2.grid(row=6, column=1, sticky="w")

        tk.Button(self, text="Lưu Khách Hàng", bg="#2563eb", fg="white", font=("Segoe UI", 10, "bold"), command=self.save_customer).pack(pady=10)

    def on_limit_change(self, event=None):
        val = self.ent_limit.get().strip()
        words = num2vietnamese_words(val)
        self.lbl_limit_words.config(text=words)

    def save_customer(self):
        try:
            name = self.ent_name.get().strip()
            if not name:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên khách hàng!")
                return

            customer_dao.add_customer(
                name,
                self.ent_phone.get().strip(),
                self.ent_addr.get().strip(),
                float(self.ent_limit.get() or config.DEFAULT_CREDIT_LIMIT),
                self.var_is_contractor.get()
            )
            messagebox.showinfo("Thành công", "Đã thêm khách hàng mới!")
            self.destroy()
            
            if self.on_success_callback:
                self.on_success_callback()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm khách hàng: {str(e)}")
