import tkinter as tk
from tkinter import ttk, messagebox
import config
from dao import vehicle_dao

class AddVehicleDialog(tk.Toplevel):
    def __init__(self, parent, on_success_callback=None):
        super().__init__(parent)
        self.on_success_callback = on_success_callback
        
        self.title("Thêm Xe & Tài Xế Bãi")
        self.geometry("380x340")
        self.grab_set()

        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self, text="Đăng Ký Xe & Tài Xế Mới", font=("Segoe UI", 12, "bold")).pack(pady=10)

        form = ttk.Frame(self, padding=10)
        form.pack(fill="both", expand=True)

        fields = [
            ("Biển số xe (vd: 60C-999.88):", "ent_plate"),
            ("Họ tên tài xế:", "ent_driver"),
            ("Số điện thoại:", "ent_phone"),
            ("Dung tích thùng xe (m³):", "ent_cap"),
            ("Thù lao cho tài xế (đ/chuyến):", "ent_pay"),
            ("Định mức xăng dầu (đ/chuyến):", "ent_fuel"),
        ]

        self.entries = {}
        for i, (label_text, var_name) in enumerate(fields):
            ttk.Label(form, text=label_text).grid(row=i, column=0, sticky="w", pady=3)
            ent = ttk.Entry(form, width=22)
            ent.grid(row=i, column=1, pady=3, sticky="ew")
            self.entries[var_name] = ent

        self.entries["ent_cap"].insert(0, str(config.DEFAULT_VEHICLE_CAPACITY))
        self.entries["ent_pay"].insert(0, "50000")
        self.entries["ent_fuel"].insert(0, "30000")

        tk.Button(self, text="Lưu Đăng Ký Xe", bg="#2563eb", fg="white", font=("Segoe UI", 10, "bold"), command=self.save_vehicle).pack(pady=10)

    def save_vehicle(self):
        try:
            vehicle_dao.add_vehicle(
                self.entries["ent_plate"].get().strip().upper(),
                self.entries["ent_driver"].get().strip(),
                self.entries["ent_phone"].get().strip(),
                float(self.entries["ent_cap"].get() or config.DEFAULT_VEHICLE_CAPACITY),
                float(self.entries["ent_pay"].get() or 50000),
                float(self.entries["ent_fuel"].get() or 30000)
            )
            messagebox.showinfo("Thành công", "Đã đăng ký thêm xe mới!")
            self.destroy()
            if self.on_success_callback:
                self.on_success_callback()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm xe: {str(e)}")
