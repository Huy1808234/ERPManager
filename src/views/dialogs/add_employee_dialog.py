import tkinter as tk
from tkinter import ttk, messagebox
from dao import employee_dao

class AddEmployeeDialog(tk.Toplevel):
    def __init__(self, parent, on_success_callback=None):
        super().__init__(parent)
        self.on_success_callback = on_success_callback
        
        self.title("Thêm Nhân Viên Mới")
        self.geometry("620x420")
        self.grab_set()

        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self, text="TẠO HỒ SƠ NHÂN VIÊN MỚI", font=("Segoe UI", 12, "bold"), foreground="#1e3a8a").pack(pady=10)

        form = ttk.Frame(self, padding=10)
        form.pack(fill="both", expand=True)

        fields = [
            ("Mã nhân viên (vd: NV006):", "ent_code"),
            ("Họ tên nhân viên:", "ent_name"),
            ("Số điện thoại:", "ent_phone"),
            ("Vị trí / Chức vụ:", "cbo_position"),
            ("Hình thức lương:", "cbo_type"),
            ("Lương cứng tháng (đ):", "ent_base"),
            ("Thù lao/chuyến (nếu là tài xế):", "ent_trip"),
            ("Phụ cấp / Thưởng (đ):", "ent_allowance"),
        ]

        self.entries = {}
        for i, (label_text, var_name) in enumerate(fields):
            ttk.Label(form, text=label_text).grid(row=i, column=0, sticky="w", pady=3)
            if var_name == "cbo_position":
                cbo = ttk.Combobox(form, width=22, state="readonly", values=[
                    "Tài xế xe ben",
                    "Lái xe múc cát/đá",
                    "Kế toán bán hàng",
                    "Quản lý bãi & Bốc xếp",
                    "Bảo vệ bãi"
                ])
                cbo.current(0)
                cbo.grid(row=i, column=1, pady=3, sticky="ew")
                self.entries[var_name] = cbo
            elif var_name == "cbo_type":
                cbo = ttk.Combobox(form, width=22, state="readonly", values=["Theo chuyến", "Lương tháng"])
                cbo.current(0)
                cbo.grid(row=i, column=1, pady=3, sticky="ew")
                self.entries[var_name] = cbo
            else:
                ent = ttk.Entry(form, width=25)
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
                    
                    # Store callback to trigger after insert
                    if not hasattr(self, 'money_callbacks'):
                        self.money_callbacks = []
                    self.money_callbacks.append(on_change)

        self.entries["ent_code"].insert(0, f"NV00{len(employee_dao.get_all_employees()) + 1}")
        self.entries["ent_base"].insert(0, "0")
        self.entries["ent_trip"].insert(0, "50000")
        self.entries["ent_allowance"].insert(0, "500000")
        
        if hasattr(self, 'money_callbacks'):
            for cb in self.money_callbacks:
                cb()

        tk.Button(self, text="💾 LƯU NHÂN VIÊN", bg="#2563eb", fg="white", font=("Segoe UI", 10, "bold"), command=self.save_emp).pack(pady=10)

    def save_emp(self):
        try:
            code = self.entries["ent_code"].get().strip()
            name = self.entries["ent_name"].get().strip()
            if not name:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên nhân viên!")
                return

            employee_dao.add_employee(
                code,
                name,
                self.entries["ent_phone"].get().strip(),
                self.entries["cbo_position"].get(),
                self.entries["cbo_type"].get(),
                float(self.entries["ent_base"].get() or 0),
                float(self.entries["ent_trip"].get() or 0),
                float(self.entries["ent_allowance"].get() or 0)
            )
            messagebox.showinfo("Thành công", f"Đã thêm hồ sơ nhân viên [{name}]!")
            self.destroy()
            
            if self.on_success_callback:
                self.on_success_callback()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm nhân viên: {str(e)}")
