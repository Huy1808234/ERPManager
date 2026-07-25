import tkinter as tk
from tkinter import ttk, messagebox
from dao import employee_dao
from utils import num2vietnamese_words

class SalaryAdvanceDialog(tk.Toplevel):
    def __init__(self, parent, emp_id, emp_name, on_success_callback=None):
        super().__init__(parent)
        self.on_success_callback = on_success_callback
        self.emp_id = emp_id
        self.emp_name = emp_name
        
        self.title("Ghi Nhận Tạm Ứng Lương")
        self.geometry("400x280")
        self.grab_set()

        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self, text=f"TẠM ỨNG LƯƠNG: {self.emp_name.upper()}", font=("Segoe UI", 12, "bold"), foreground="#059669").pack(pady=10)

        form = ttk.Frame(self, padding=10)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text="Số tiền tạm ứng (đ):").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_amount = ttk.Entry(form, width=25)
        self.ent_amount.insert(0, "1000000")
        self.ent_amount.grid(row=0, column=1, pady=5)

        ttk.Label(form, text="Bằng chữ:").grid(row=1, column=0, sticky="w", pady=5)
        self.lbl_words = ttk.Label(form, text="Một triệu đồng", font=("Segoe UI", 9, "italic", "bold"), foreground="#0369a1")
        self.lbl_words.grid(row=1, column=1, sticky="w", pady=5)

        self.ent_amount.bind("<KeyRelease>", self.on_amount_change)

        ttk.Label(form, text="Ghi chú lý do ứng:").grid(row=2, column=0, sticky="w", pady=5)
        self.ent_note = ttk.Entry(form, width=25)
        self.ent_note.insert(0, "Ứng lương giữa tháng")
        self.ent_note.grid(row=2, column=1, pady=5)

        tk.Button(self, text="💾 GHI NHẬN TẠM ỨNG", bg="#059669", fg="white", font=("Segoe UI", 10, "bold"), command=self.save_advance).pack(pady=10)

    def on_amount_change(self, event=None):
        val = self.ent_amount.get().strip()
        self.lbl_words.config(text=num2vietnamese_words(val))

    def save_advance(self):
        try:
            amount = float(self.ent_amount.get() or 0)
            note = self.ent_note.get()

            employee_dao.record_salary_advance(self.emp_id, amount, note)
            messagebox.showinfo("Thành công", f"Đã ghi nhận tạm ứng {amount:,.0f}đ cho nhân viên {self.emp_name}!")
            self.destroy()
            
            if self.on_success_callback:
                self.on_success_callback()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể ghi nhận tạm ứng: {str(e)}")
