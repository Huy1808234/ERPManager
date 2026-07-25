import tkinter as tk
from tkinter import ttk, messagebox
from dao import employee_dao

class EditEmployeeDialog(tk.Toplevel):
    def __init__(self, parent, employee, on_success_callback=None):
        super().__init__(parent)
        self.on_success_callback = on_success_callback
        self.employee = employee
        
        self.title("Sửa Hồ Sơ Nhân Viên")
        self.geometry("620x420")
        self.grab_set()

        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self, text="CẬP NHẬT LƯƠNG & HỒ SƠ NHÂN VIÊN", font=("Segoe UI", 12, "bold"), foreground="#d97706").pack(pady=10)

        form = ttk.Frame(self, padding=10)
        form.pack(fill="both", expand=True)

        e = self.employee
        fields = [
            ("Mã nhân viên:", "ent_code", e['code']),
            ("Họ tên nhân viên:", "ent_name", e['name']),
            ("Số điện thoại:", "ent_phone", e['phone'] or ""),
            ("Vị trí / Chức vụ:", "cbo_position", e['position']),
            ("Hình thức lương:", "cbo_type", e['salary_type']),
            ("Lương cứng tháng (đ):", "ent_base", str(int(e['base_salary']))),
            ("Thù lao/chuyến (đ):", "ent_trip", str(int(e['pay_per_trip']))),
            ("Phụ cấp / Thưởng (đ):", "ent_allowance", str(int(e['allowance']))),
        ]

        self.entries = {}
        for i, (label_text, var_name, default_val) in enumerate(fields):
            ttk.Label(form, text=label_text).grid(row=i, column=0, sticky="w", pady=3)
            if var_name == "cbo_position":
                cbo = ttk.Combobox(form, width=22, state="readonly", values=[
                    "Tài xế xe ben",
                    "Lái xe múc cát/đá",
                    "Kế toán bán hàng",
                    "Quản lý bãi & Bốc xếp",
                    "Bảo vệ bãi"
                ])
                cbo.set(default_val)
                cbo.grid(row=i, column=1, pady=3, sticky="ew")
                self.entries[var_name] = cbo
            elif var_name == "cbo_type":
                cbo = ttk.Combobox(form, width=22, state="readonly", values=["Theo chuyến", "Lương tháng"])
                cbo.set(default_val)
                cbo.grid(row=i, column=1, pady=3, sticky="ew")
                self.entries[var_name] = cbo
            else:
                ent = ttk.Entry(form, width=25)
                ent.insert(0, default_val)
                ent.grid(row=i, column=1, pady=3, sticky="ew")
                self.entries[var_name] = ent
                
                if var_name in ["ent_base", "ent_trip", "ent_allowance"]:
                    lbl_money = tk.Label(form, text="", font=("Segoe UI", 9, "italic"), fg="#059669")
                    lbl_money.grid(row=i, column=2, sticky="w", padx=10)
                    
                    def make_on_change(ent_widget, lbl_widget):
                        def on_change(e=None):
                            from utils import num2vietnamese_words
                            val = ent_widget.get().replace(",", "")
                            lbl_widget.config(text=num2vietnamese_words(val))
                        return on_change

                    on_change = make_on_change(ent, lbl_money)
                    ent.bind("<KeyRelease>", on_change)
                    on_change() # Init text

        tk.Button(self, text="💾 CẬP NHẬT HỒ SƠ", bg="#d97706", fg="white", font=("Segoe UI", 10, "bold"), command=self.update_emp).pack(pady=10)

    def update_emp(self):
        try:
            code = self.entries["ent_code"].get().strip()
            name = self.entries["ent_name"].get().strip()
            if not name:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên nhân viên!")
                return

            employee_dao.update_employee(
                self.employee['id'],
                code,
                name,
                self.entries["ent_phone"].get().strip(),
                self.entries["cbo_position"].get(),
                self.entries["cbo_type"].get(),
                float(self.entries["ent_base"].get() or 0),
                float(self.entries["ent_trip"].get() or 0),
                float(self.entries["ent_allowance"].get() or 0)
            )
            messagebox.showinfo("Thành công", f"Đã cập nhật hồ sơ nhân viên [{name}]!")
            self.destroy()
            
            if self.on_success_callback:
                self.on_success_callback()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật nhân viên: {str(e)}")
